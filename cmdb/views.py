from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.db.models import Q
from django.core.paginator import Paginator
from django.db import connection
from . import models, models_view, forms
import json, csv, codecs, time
import logging
from django.contrib.auth.decorators import login_required

from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.

# 在APP中调用日志模块
logger = logging.getLogger('cmdb.view')


# 主页
@login_required(login_url='/users/login/')
def index(request):
    return render(request, 'cmdb/index.html')

class TableView(LoginRequiredMixin, ListView):
    login_url = '/users/login/'
    model = models_view.Resource_Info
    template_name = 'cmdb/tables.html'
    context_object_name = 'page_data'

    # 在基于类的通用视图：ListView和DetailView中的内容，我们已将视图函数转换成了类视图。而类视图ListView已经帮我们写好了上述的分页逻辑，
    # 我们只需通过指定paginate_by属性来开启分页功能即可，即在类视图中指定paginate_by属性的值
    paginate_by = 20

    def get_paginate_by(self, queryset):
        """
        接收GET请求的每页数量重新赋值.
        """
        rownum = self.request.GET.get('rownum')
        if rownum:
            self.request.session["rownum"] = rownum
            self.paginate_by = rownum
        elif self.request.session.get('rownum', None):
            self.paginate_by = self.request.session["rownum"]

        return self.paginate_by

    def get_queryset(self):
        """
        接收GET请求中的项目/系统名称重新过滤.
        """
        pid = self.request.GET.get('pid')
        aid = self.request.GET.get('aid')
        page = self.request.GET.get('page')

        if pid:
            self.request.session["pid"] = pid
            return super(TableView, self).get_queryset().filter(projname=pid)
        elif aid:
            self.request.session["aid"] = aid
            return super(TableView, self).get_queryset().filter(appsystem=aid)
        elif page or self.request.GET.get('rownum'):
            if self.request.session.get('pid', None):
                pid = self.request.session["pid"]
                return super(TableView, self).get_queryset().filter(projname=pid)
            elif self.request.session.get('aid', None):
                aid = self.request.session["aid"]
                return super(TableView, self).get_queryset().filter(appsystem=aid)
            else:
                return super(TableView, self).get_queryset()
        else:
            if self.request.session.get('pid', None):
                del self.request.session["pid"]
            if self.request.session.get('aid', None):
                del self.request.session["aid"]
            if self.request.session.get('rownum', None):
                del self.request.session["rownum"]

            return super(TableView, self).get_queryset()

    def get_context_data(self, **kwargs):
        """
        在视图函数中将模板变量传递给模板是通过给 render 函数的 context 参数传递一个字典实现的，
        例如 render(request, 'blog/index.html', context={'post_list': post_list})，
        这里传递了一个 {'post_list': post_list} 字典给模板。
        在类视图中，这个需要传递的模板变量字典是通过 get_context_data 获得的，
        所以我们复写该方法，以便我们能够自己再插入一些我们自定义的模板变量进去。
        """

        # 首先获得父类生成的传递给模板的字典。
        context = super().get_context_data(**kwargs)

        # 父类生成的字典中已有 paginator、page_obj、is_paginated 这三个模板变量，
        # paginator 是 Paginator 的一个实例，
        # page_obj 是 Page 的一个实例，
        # is_paginated 是一个布尔变量，用于指示是否已分页。
        # 例如如果规定每页 10 个数据，而本身只有 5 个数据，其实就用不着分页，此时 is_paginated=False。
        # 关于什么是 Paginator，Page 类在 Django Pagination 简单分页：http://zmrenwu.com/post/34/ 中已有详细说明。
        # 由于 context 是一个字典，所以调用 get 方法从中取出某个键对应的值。
        paginator = context.get('paginator')
        page = context.get('page_obj')
        is_paginated = context.get('is_paginated')

        # 调用自己写的 pagination_data 方法获得显示分页导航条需要的数据，见下方。
        pagination_data = self.pagination_data(paginator, page, is_paginated)

        # 将分页导航条的模板变量更新到 context 中，注意 pagination_data 方法返回的也是一个字典。
        context.update(pagination_data)

        # 记录用户自定义每页显示行数；
        if self.request.session.get('rownum', None):
            context['rownum'] = self.request.session["rownum"]

        # 将更新后的 context 返回，以便 ListView 使用这个字典中的模板变量去渲染模板。
        # 注意此时 context 字典中已有了显示分页导航条所需的数据。
        return context

    def pagination_data(self, paginator, page, is_paginated):
        if not is_paginated:
            # 如果没有分页，则无需显示分页导航条，不用任何分页导航条的数据，因此返回一个空的字典
            return {}

        # 当前页左边连续的页码号，初始值为空
        left = []

        # 当前页右边连续的页码号，初始值为空
        right = []

        # 标示第 1 页页码后是否需要显示省略号
        left_has_more = False

        # 标示最后一页页码前是否需要显示省略号
        right_has_more = False

        # 标示是否需要显示第 1 页的页码号。
        # 因为如果当前页左边的连续页码号中已经含有第 1 页的页码号，此时就无需再显示第 1 页的页码号，
        # 其它情况下第一页的页码是始终需要显示的。
        # 初始值为 False
        first = False

        # 标示是否需要显示最后一页的页码号。
        # 需要此指示变量的理由和上面相同。
        last = False

        # 获得用户当前请求的页码号
        page_number = page.number

        # 获得分页后的总页数
        total_pages = paginator.num_pages

        # 获得整个分页页码列表，比如分了四页，那么就是 [1, 2, 3, 4]
        page_range = paginator.page_range

        if page_number == 1:
            # 如果用户请求的是第一页的数据，那么当前页左边的不需要数据，因此 left=[]（已默认为空）。
            # 此时只要获取当前页右边的连续页码号，
            # 比如分页页码列表是 [1, 2, 3, 4]，那么获取的就是 right = [2, 3]。
            # 注意这里只获取了当前页码后连续两个页码，你可以更改这个数字以获取更多页码。
            right = page_range[page_number:page_number + 2]

            # 如果最右边的页码号比最后一页的页码号减去 1 还要小，
            # 说明最右边的页码号和最后一页的页码号之间还有其它页码，因此需要显示省略号，通过 right_has_more 来指示。
            if right[-1] < total_pages - 1:
                right_has_more = True

            # 如果最右边的页码号比最后一页的页码号小，说明当前页右边的连续页码号中不包含最后一页的页码
            # 所以需要显示最后一页的页码号，通过 last 来指示
            if right[-1] < total_pages:
                last = True

        elif page_number == total_pages:
            # 如果用户请求的是最后一页的数据，那么当前页右边就不需要数据，因此 right=[]（已默认为空），
            # 此时只要获取当前页左边的连续页码号。
            # 比如分页页码列表是 [1, 2, 3, 4]，那么获取的就是 left = [2, 3]
            # 这里只获取了当前页码后连续两个页码，你可以更改这个数字以获取更多页码。
            left = page_range[(page_number - 3) if (page_number - 3) > 0 else 0:page_number - 1]

            # 如果最左边的页码号比第 2 页页码号还大，
            # 说明最左边的页码号和第 1 页的页码号之间还有其它页码，因此需要显示省略号，通过 left_has_more 来指示。
            if left[0] > 2:
                left_has_more = True

            # 如果最左边的页码号比第 1 页的页码号大，说明当前页左边的连续页码号中不包含第一页的页码，
            # 所以需要显示第一页的页码号，通过 first 来指示
            if left[0] > 1:
                first = True
        else:
            # 用户请求的既不是最后一页，也不是第 1 页，则需要获取当前页左右两边的连续页码号，
            # 这里只获取了当前页码前后连续两个页码，你可以更改这个数字以获取更多页码。
            left = page_range[(page_number - 3) if (page_number - 3) > 0 else 0:page_number - 1]
            right = page_range[page_number:page_number + 2]

            # 是否需要显示最后一页和最后一页前的省略号
            if right[-1] < total_pages - 1:
                right_has_more = True
            if right[-1] < total_pages:
                last = True

            # 是否需要显示第 1 页和第 1 页后的省略号
            if left[0] > 2:
                left_has_more = True
            if left[0] > 1:
                first = True

        data = {
            'left': left,
            'right': right,
            'left_has_more': left_has_more,
            'right_has_more': right_has_more,
            'page_number': page.number,
            'first': first,
            'last': last,
        }

        return data

# 资源搜索
class SearchView(TableView):
    def get_queryset(self):
        """
        搜索 应用名称|联系人|软件名称|软件类型|设备别名|设备IP
        :return:
        """
        text = self.request.GET.get('text').strip()
        return super(SearchView, self).get_queryset().filter(Q(appsystem__icontains=text) |
                                                            Q(appcontactname__icontains=text) |
                                                            Q(sname__icontains=text) |
                                                            Q(stype__icontains=text) |
                                                            Q(devnamealias__icontains=text) |
                                                            Q(devip__icontains=text))

# 资源新增页面
def resadd(request):
    if request.method == "GET":
        projform = forms.ProjectFrom()
        devform = forms.DeviceForm()
        softform = forms.SoftwareFrom()
        relform = forms.RelationsFrom()
        return render(request, 'cmdb/resadd.html', locals())

    if request.method == "POST":
        projform = forms.ProjectFrom(request.POST)
        if projform.is_valid():
            projadd = projform.save(commit=False)
            projadd.save()

        devform = forms.DeviceForm(request.POST)
        if devform.is_valid():
            devadd = devform.save(commit=False)
            devadd.save()

        softform = forms.SoftwareFrom(request.POST)
        if softform.is_valid():
            softadd = softform.save(commit=False)
            softadd.save()

        relform = forms.RelationsFrom(request.POST)
        if relform.is_valid():
            reladd = relform.save(commit=False)
            reladd.save()

        return redirect('/cmdb/tables')


# 资源编辑页面
def resedit(request):
    id = request.GET.get('id').replace('None', '0')
    if int(id.split("_")[0]) > 0:
        pid = id.split("_")[0]
        proj_info = models.ProjectInfo.objects.get(pid=pid)
    if int(id.split("_")[1]) > 0:
        devid = id.split("_")[1]
        dev_info = models.DeviceInfo.objects.get(devid=devid)
    if int(id.split("_")[2]) > 0:
        sid = id.split("_")[2]
        soft_info = models.SoftwareInfo.objects.get(sid=sid)
    if int(id.split("_")[3]) > 0:
        rid = id.split("_")[3]
        rel_info = models.Relations.objects.get(rid=rid)

    if request.method == "GET":
        try:
            projform = forms.ProjectFrom(instance=proj_info)
        except Exception as e:
            relform = forms.RelationsFrom()
        try:
            devform = forms.DeviceForm(instance=dev_info)
        except Exception as e:
            relform = forms.RelationsFrom()
        try:
            softform = forms.SoftwareFrom(instance=soft_info)
        except Exception as e:
            relform = forms.RelationsFrom()
        try:
            relform = forms.RelationsFrom(instance=rel_info)
        except Exception as e:
            relform = forms.RelationsFrom()
        return render(request, 'cmdb/resedit.html', locals())

    if request.method == "POST":
        try:
            projform = forms.ProjectFrom(request.POST, instance=proj_info)
        except Exception as e:
            logger.error(e)
        else:
            if projform.is_valid():
                projadd = projform.save(commit=False)
                projadd.save()

        try:
            devform = forms.DeviceForm(request.POST, instance=dev_info)
        except Exception as e:
            logger.error(e)
        else:
            if devform.is_valid():
                devadd = devform.save(commit=False)
                devadd.save()

        try:
            softform = forms.SoftwareFrom(request.POST, instance=soft_info)
        except Exception as e:
            logger.error(e)
        else:
            if softform.is_valid():
                softadd = softform.save(commit=False)
                softadd.save()

        try:
            relform = forms.RelationsFrom(request.POST, instance=rel_info)
        except Exception as e:
            logger.error(e)
        else:
            if relform.is_valid():
                reladd = relform.save(commit=False)
                reladd.save()

        return redirect('/cmdb/tables')

# 删除资源信息
def resdel(request):
    if request.method == "GET":
        id = request.GET.get('id').split("@")
        deltype = str(request.GET.get('deltype'))
        for item in id:
            item = item.replace('None', '0')
            if int(item.split("_")[2]) > 0 and deltype == "1":
                sid = item.split("_")[2]
                try:
                    models.SoftwareInfo.objects.filter(sid=sid).delete()
                except Exception as e:
                    logger.error(e)
            if int(item.split("_")[3]) > 0 and deltype == "2":
                rid = item.split("_")[3]
                try:
                    models.Relations.objects.filter(rid=rid).delete()
                except Exception as e:
                    logger.error(e)
            if int(item.split("_")[1]) > 0 and deltype == "3":
                devid = item.split("_")[1]
                try:
                    models.DeviceInfo.objects.filter(devid=devid).delete()
                except Exception as e:
                    logger.error(e)
            if int(item.split("_")[0]) > 0 and deltype == "4":
                pid = item.split("_")[0]
                try:
                    models.ProjectInfo.objects.filter(pid=pid).delete()
                except Exception as e:
                    logger.error(e)

    # 返回资产信息页面
    return redirect('/cmdb/tables')

# +----------------------------------------------------Echart图表-------------------------------------------------+
# 业务关系图
@login_required(login_url='/users/login/')
def topchart(request):
    return render(request, 'cmdb/topchart.html', locals())


def jsondata(request):
    if request.method == "GET":
        # 构造legendes数据
        legendes = []
        proj_list = models.ProjectInfo.objects.values_list('projname', flat=True).distinct()
        legendes = list(proj_list)

        # 构造categories数据
        categories = []
        for item in legendes:
            data = {
                'name': item
            }
            categories.append(data)

        # 构造dataList数据
        ips = models.DeviceInfo.objects.values_list('devip', flat=True).distinct()
        dataList = []
        for ip in ips:
            for index, projname in enumerate(legendes):
                ipproj = models_view.Resource_Info.objects.filter(devip=ip).values_list('projname', flat=True)[0]
                if ipproj == projname:
                    category = int(index)
                    break

            data = {
                'name': ip,
                'category': category,
                'draggable': 'true',
                'value': int(index) + 1,
            }
            dataList.append(data)

        # 构造linkList数据
        cursor = connection.cursor()
        cursor.execute(
            "SELECT source, target, sname from ( "
            "SELECT sname, devip AS source, upip AS target FROM t_cmdb_relations r "
            "LEFT JOIN t_cmdb_device_info d ON r.drdevip_id=d.devid AND LENGTH(r.upip) > 0 "
            "LEFT JOIN t_cmdb_software_info s ON r.srsname_id=s.sid "
            "UNION "
            "SELECT sname, downip, devip FROM t_cmdb_relations r "
            "LEFT JOIN t_cmdb_device_info d ON r.drdevip_id=d.devid AND LENGTH(r.downip) > 0 "
            "LEFT JOIN t_cmdb_software_info s ON r.srsname_id=s.sid "
            ") t "
            "WHERE LENGTH(source) > 0 OR LENGTH(target) > 0")
        link_info = cursor.fetchall()
        linkList = []
        for item in link_info:
            link = {
                'source': item[0],
                'target': item[1],
                'value': item[2],
            }
            linkList.append(link)

        # 构造完整Json数据
        tmpstr = {
            'legendes': legendes,
            'categories': categories,
            'data': dataList,
            'links': linkList
        }
        jsonData = json.dumps(tmpstr)
    return HttpResponse(jsonData)
# +----------------------------------------------------CSV导入/导出-------------------------------------------------+
# 导入CSV文件
def uploadfile(request):
    if request.POST:
        form = forms.UploadFileForm(request.POST, request.FILES)
        f = request.FILES['file']
        line = f.readline()  # 读取表头
        while True:
            line = f.readline()
            try:
                line1 = line.decode('gb2312')
                if not line1 or line1 == '\r\n' or line1 == '\r' or line1 == '\n' or line1 == '': break
                arg = line1.split(',')
                arg[32] = arg[32].rstrip('\r\n')
                # 写入项目系统表
                if arg[2]:
                    result = models.ProjectInfo.objects.filter(appsystem=arg[2])
                    if result:
                        models.ProjectInfo.objects.filter(appsystem=arg[2]).update(projname=arg[1], appsystem=arg[2],
                                                                                   projdesc=arg[20],
                                                                                   projcontactname=arg[21],
                                                                                   projcontactphone=arg[22],
                                                                                   projcontactemail=arg[23],
                                                                                   appcontactname=arg[24],
                                                                                   appcontactphone=arg[25],
                                                                                   appcontactemail=arg[26],
                                                                                   groupname=arg[27])
                    else:
                        proj = models.ProjectInfo.objects.create(projname=arg[1], appsystem=arg[2], projdesc=arg[20],
                                                                 projcontactname=arg[21], projcontactphone=arg[22],
                                                                 projcontactemail=arg[23], appcontactname=arg[24],
                                                                 appcontactphone=arg[25], appcontactemail=arg[26],
                                                                 groupname=arg[27])
                        proj.save()

                # 写入设备表
                if arg[3]:
                    result = models.DeviceInfo.objects.filter(devip=arg[3])
                    if arg[28] == '': arg[28] = 0
                    if arg[29] == '': arg[29] = 0
                    if arg[30] == '': arg[30] = 0
                    if arg[31] == '': arg[31] = 0
                    if result:
                        models.DeviceInfo.objects.filter(devip=arg[3]).update(devip=arg[3], devname=arg[4],
                                                                              devnamealias=arg[5], ostype=arg[6],
                                                                              devtype=arg[7], devstatus=arg[8],
                                                                              cpusize=arg[28], cpucorecount=arg[29],
                                                                              memsize=arg[30], disksize=arg[31],
                                                                              location=arg[32], devdesc=arg[9])
                    else:
                        device = models.DeviceInfo.objects.create(devip=arg[3], devname=arg[4], devnamealias=arg[5],
                                                                  ostype=arg[6], devtype=arg[7], devstatus=arg[8],
                                                                  cpusize=arg[28], cpucorecount=arg[29],
                                                                  memsize=arg[30], disksize=arg[31], location=arg[32],
                                                                  devdesc=arg[9])
                        device.save()

                # 写入软件表
                if arg[10]:
                    # 取回应用系统ID
                    pidstr = str(models.ProjectInfo.objects.filter(appsystem=arg[2]).values_list('pid', flat=True)[0])
                    # 取回设备ID
                    devidstr = str(models.DeviceInfo.objects.filter(devip=arg[3]).values_list('devid', flat=True)[0])

                    result = models.SoftwareInfo.objects.filter(Q(dsdevip_id=devidstr) & Q(sname=arg[10]) &
                                                                Q(sport=arg[12]))
                    if result:
                        models.SoftwareInfo.objects.filter(Q(dsdevip_id=devidstr) & Q(sname=arg[10]) &
                                                           Q(sport=arg[12])).update(stype=arg[11], sversion=arg[13],
                                                                                    spath=arg[14], sdesc=arg[15],
                                                                                    psappsystem_id=pidstr)
                    else:
                        soft = models.SoftwareInfo.objects.create(dsdevip_id=devidstr, sname=arg[10], stype=arg[11],
                                                                  sport=arg[12],
                                                                  sversion=arg[13], spath=arg[14], sdesc=arg[15],
                                                                  psappsystem_id=pidstr)
                        soft.save()

                # 写入关联表
                if arg[16] or arg[18]:
                    # 取回设备ID
                    devidstr = str(models.DeviceInfo.objects.filter(devip=arg[3]).values_list('devid', flat=True)[0])
                    # 取回软件ID
                    try:
                        sidstr = str(models.SoftwareInfo.objects.filter(
                            Q(dsdevip_id=devidstr) & Q(sname=arg[10]) & Q(sport=arg[12])).values_list('sid', flat=True)[
                                         0])
                    except:
                        sidstr = 1

                    reltmp = models.Relations.objects.filter(
                        Q(drdevip_id=devidstr) & Q(srsname_id=sidstr) & Q(upip=arg[16]) & Q(downip=arg[18]))
                    reltmpu = models.Relations.objects.filter(
                        Q(drdevip_id=devidstr) & Q(srsname_id=sidstr) & Q(upip=arg[16]))
                    reltmpd = models.Relations.objects.filter(
                        Q(drdevip_id=devidstr) & Q(srsname_id=sidstr) & Q(downip=arg[18]))

                    if reltmp:
                        models.Relations.objects.filter(Q(drdevip_id=devidstr) & Q(srsname_id=sidstr) & Q(upip=arg[16])
                                                        & Q(downip=arg[18])).update(updesc=arg[17], downdesc=arg[19])
                    elif reltmpu:
                        models.Relations.objects.filter(Q(drdevip_id=devidstr) & Q(srsname_id=sidstr) & Q(upip=arg[16])
                                                        ).update(updesc=arg[17], downip=arg[18], downdesc=arg[19])
                    elif reltmpd:
                        models.Relations.objects.filter(Q(drdevip_id=devidstr) & Q(srsname_id=sidstr) &
                                                        Q(downip=arg[18])).update(upip=arg[16], updesc=arg[17],
                                                                                  downdesc=arg[19])
                    else:
                        rel = models.Relations.objects.create(upip=arg[16], updesc=arg[17], downip=arg[18],
                                                              downdesc=arg[19], drdevip_id=devidstr, srsname_id=sidstr)
                        rel.save()

                # 写入多对多中间表
                if arg[3]:
                    # 取回应用系统ID、设备ID、软件对应设备的系统ID
                    pidstr = str(models.ProjectInfo.objects.filter(appsystem=arg[2]).values_list('pid', flat=True)[0])
                    devidstr = str(models.DeviceInfo.objects.filter(devip=arg[3]).values_list('devid', flat=True)[0])
                    try:
                        psidstr = str(models.SoftwareInfo.objects.filter(Q(dsdevip_id=devidstr) & Q(sname=arg[10]) &
                                                                         Q(sport=arg[12])).values_list('psappsystem_id',
                                                                                                       flat=True)[0])
                        print(psidstr)
                    except Exception as e:
                        logger.error(e)
                        psidstr = ''

                    try:
                        pdidstr = str(models.DpMap.objects.filter(deviceinfo_id=devidstr).values_list('projectinfo_id',
                                                                                                      flat=True)[0])
                    except Exception as e:
                        logger.error(e)
                        pdidstr = ''

                    # 开始操作多对多中间表
                    if models.DpMap.objects.filter(Q(deviceinfo_id=devidstr) & Q(projectinfo_id=pidstr)):
                        pass
                    else:
                        if (psidstr and psidstr == pdidstr) and pidstr != pdidstr:
                            # 更新多对多中间表
                            models.DpMap.objects.filter(deviceinfo_id=devidstr).update(projectinfo_id=pidstr)
                        else:
                            # 写入多对多中间表
                            dpmap = models.DpMap.objects.create(deviceinfo_id=devidstr, projectinfo_id=pidstr)
                            dpmap.save()


            except Exception as e:
                logger.error(e)
                line2 = line.decode('utf-8-sig')
                if not line1 or line1 == '\r\n' or line1 == '\r' or line1 == '\n' or line1 == '': break
                arg = line1.split(',')
                arg[32] = arg[32].rstrip('\r\n')
                # 写入项目系统表
                if arg[2]:
                    result = models.ProjectInfo.objects.filter(appsystem=arg[2])
                    if result:
                        models.ProjectInfo.objects.filter(appsystem=arg[2]).update(projname=arg[1], appsystem=arg[2],
                                                                                   projdesc=arg[20],
                                                                                   projcontactname=arg[21],
                                                                                   projcontactphone=arg[22],
                                                                                   projcontactemail=arg[23],
                                                                                   appcontactname=arg[24],
                                                                                   appcontactphone=arg[25],
                                                                                   appcontactemail=arg[26],
                                                                                   groupname=arg[27])
                    else:
                        proj = models.ProjectInfo.objects.create(projname=arg[1], appsystem=arg[2], projdesc=arg[20],
                                                                 projcontactname=arg[21], projcontactphone=arg[22],
                                                                 projcontactemail=arg[23], appcontactname=arg[24],
                                                                 appcontactphone=arg[25], appcontactemail=arg[26],
                                                                 groupname=arg[27])
                        proj.save()

                # 写入设备表
                if arg[3]:
                    result = models.DeviceInfo.objects.filter(devip=arg[3])
                    if arg[28] == '': arg[28] = 0
                    if arg[29] == '': arg[29] = 0
                    if arg[30] == '': arg[30] = 0
                    if arg[31] == '': arg[31] = 0
                    if result:
                        models.DeviceInfo.objects.filter(devip=arg[3]).update(devip=arg[3], devname=arg[4],
                                                                              devnamealias=arg[5], ostype=arg[6],
                                                                              devtype=arg[7], devstatus=arg[8],
                                                                              cpusize=arg[28], cpucorecount=arg[29],
                                                                              memsize=arg[30], disksize=arg[31],
                                                                              location=arg[32], devdesc=arg[9])
                    else:
                        device = models.DeviceInfo.objects.create(devip=arg[3], devname=arg[4], devnamealias=arg[5],
                                                                  ostype=arg[6], devtype=arg[7], devstatus=arg[8],
                                                                  cpusize=arg[28], cpucorecount=arg[29],
                                                                  memsize=arg[30], disksize=arg[31], location=arg[32],
                                                                  devdesc=arg[9])
                        device.save()

                # 写入软件表
                if arg[10]:
                    # 取回应用系统ID
                    pidstr = str(models.ProjectInfo.objects.filter(appsystem=arg[2]).values_list('pid', flat=True)[0])
                    # 取回设备ID
                    devidstr = str(models.DeviceInfo.objects.filter(devip=arg[3]).values_list('devid', flat=True)[0])

                    result = models.SoftwareInfo.objects.filter(Q(dsdevip_id=devidstr) & Q(sname=arg[10]) &
                                                                Q(sport=arg[12]))
                    if result:
                        models.SoftwareInfo.objects.filter(Q(dsdevip_id=devidstr) & Q(sname=arg[10]) &
                                                           Q(sport=arg[12])).update(stype=arg[11], sversion=arg[13],
                                                                                    spath=arg[14], sdesc=arg[15],
                                                                                    psappsystem_id=pidstr)
                    else:
                        soft = models.SoftwareInfo.objects.create(dsdevip_id=devidstr, sname=arg[10], stype=arg[11],
                                                                  sport=arg[12],
                                                                  sversion=arg[13], spath=arg[14], sdesc=arg[15],
                                                                  psappsystem_id=pidstr)
                        soft.save()

                # 写入关联表
                if arg[16] or arg[18]:
                    # 取回设备ID
                    devidstr = str(models.DeviceInfo.objects.filter(devip=arg[3]).values_list('devid', flat=True)[0])
                    # 取回软件ID
                    try:
                        sidstr = str(models.SoftwareInfo.objects.filter(
                            Q(dsdevip_id=devidstr) & Q(sname=arg[10]) & Q(sport=arg[12])).values_list('sid', flat=True)[
                                         0])
                    except:
                        sidstr = 1

                    reltmp = models.Relations.objects.filter(
                        Q(drdevip_id=devidstr) & Q(srsname_id=sidstr) & Q(upip=arg[16]) & Q(downip=arg[18]))
                    reltmpu = models.Relations.objects.filter(
                        Q(drdevip_id=devidstr) & Q(srsname_id=sidstr) & Q(upip=arg[16]))
                    reltmpd = models.Relations.objects.filter(
                        Q(drdevip_id=devidstr) & Q(srsname_id=sidstr) & Q(downip=arg[18]))

                    if reltmp:
                        models.Relations.objects.filter(Q(drdevip_id=devidstr) & Q(srsname_id=sidstr) & Q(upip=arg[16])
                                                        & Q(downip=arg[18])).update(updesc=arg[17], downdesc=arg[19])
                    elif reltmpu:
                        models.Relations.objects.filter(Q(drdevip_id=devidstr) & Q(srsname_id=sidstr) & Q(upip=arg[16])
                                                        ).update(updesc=arg[17], downip=arg[18], downdesc=arg[19])
                    elif reltmpd:
                        models.Relations.objects.filter(Q(drdevip_id=devidstr) & Q(srsname_id=sidstr) &
                                                        Q(downip=arg[18])).update(upip=arg[16], updesc=arg[17],
                                                                                  downdesc=arg[19])
                    else:
                        rel = models.Relations.objects.create(upip=arg[16], updesc=arg[17], downip=arg[18],
                                                              downdesc=arg[19], drdevip_id=devidstr, srsname_id=sidstr)
                        rel.save()

                # 写入多对多中间表
                if arg[3]:
                    # 取回应用系统ID、设备ID、软件对应设备的系统ID
                    pidstr = str(models.ProjectInfo.objects.filter(appsystem=arg[2]).values_list('pid', flat=True)[0])
                    devidstr = str(models.DeviceInfo.objects.filter(devip=arg[3]).values_list('devid', flat=True)[0])
                    try:
                        psidstr = str(models.SoftwareInfo.objects.filter(Q(dsdevip_id=devidstr) & Q(sname=arg[10]) &
                                                                         Q(sport=arg[12])).values_list('psappsystem_id',
                                                                                                       flat=True)[0])
                        print(psidstr)
                    except Exception as e:
                        logger.error(e)
                        psidstr = ''

                    try:
                        pdidstr = str(models.DpMap.objects.filter(deviceinfo_id=devidstr).values_list('projectinfo_id',
                                                                                                      flat=True)[0])
                    except Exception as e:
                        logger.error(e)
                        pdidstr = ''

                    # 开始操作多对多中间表
                    if models.DpMap.objects.filter(Q(deviceinfo_id=devidstr) & Q(projectinfo_id=pidstr)):
                        pass
                    else:
                        if (psidstr and psidstr == pdidstr) and pidstr != pdidstr:
                            # 更新多对多中间表
                            models.DpMap.objects.filter(deviceinfo_id=devidstr).update(projectinfo_id=pidstr)
                        else:
                            # 写入多对多中间表
                            dpmap = models.DpMap.objects.create(deviceinfo_id=devidstr, projectinfo_id=pidstr)
                            dpmap.save()

        f.close()
        # return render(request, 'cmdb/success.html')
        # 返回资产信息页面
        return redirect('/cmdb/tables')

    else:
        form = forms.UploadFileForm()
        return render(request, 'cmdb/upload.html', {'form': form})


# 导出CSV文件
def downloadfile(request):
    response = HttpResponse(content_type='text/csv')
    response.write(codecs.BOM_UTF8)
    csvname = "Resource_" + str(time.strftime("%Y-%m-%d", time.localtime())) + '.csv'
    response['Content-Disposition'] = 'attachment; filename=' + csvname
    writer = csv.writer(response)
    writer.writerow(
        ['ID', '项目名称', '应用系统', '设备IP地址', '设备名称', '设备别名', '操作系统', '设备类型', '设备状态','设备描述', '软件名称', '软件类型',
         '软件端口', '版本', '路径', '软件描述', '上联设备', '上联描述', '下联设备', '下联描述', '项目描述', '项目联系人姓名',
         '项目联系人电话', '项目联系人邮箱', '应用联系人姓名', '应用联系人电话', '应用联系人邮箱', '小组名称', 'CPU大小(GHz)',
         'CPU核数', '内存大小(GB)', '磁盘容量(GB)', '机房位置'])
    res_info = models_view.Resource_Info.objects.all()
    id = 0
    for line in res_info:
        id = id + 1
        # if line.dev_id:
        #     try:
        #         readName = Reader.objects.get(id__iexact=book.reader_id).name
        #     except:
        #         readName = ''
        # else:
        #     readName = ''
        writer.writerow(
            [id, line.projname, line.appsystem, line.devip, line.devname, line.devnamealias, line.ostype, line.devtype,
             line.devstatus,line.devdesc, line.sname, line.stype, line.sport, line.sversion, line.spath, line.sdesc,
             line.upip,line.updesc, line.downip, line.downdesc, line.projdesc, line.projcontactname,
             line.projcontactphone,line.projcontactemail, line.appcontactname, line.appcontactphone,
             line.appcontactemail, line.groupname,line.cpusize, line.cpucorecount, line.memsize, line.disksize,
             line.location])
    return response

# +----------------------------------------------------主机管理-------------------------------------------------+
# 查看主机信息
@login_required(login_url='/users/login/')
def hosts(request):
    if request.method == "GET":
        rownum = request.GET.get('rownum')
        text = request.GET.get('text')

        # 分页
        if text:
            results = models.DeviceInfo.objects.filter(Q(devnamealias__icontains=text) | Q(devip__icontains=text))
            limit = 20
        elif rownum:
            results = models.DeviceInfo.objects.all()
            limit = rownum
        else:
            results = models.DeviceInfo.objects.all()
            limit = 20
        paginator = Paginator(results, limit)  # 按每页10条分页
        page = request.GET.get('page', '1')  # 默认跳转到第一页
        page_data = paginator.page(page)

        # 应用机构
        projset = models.ProjectInfo.objects.values('projname').distinct()
        appset = models.ProjectInfo.objects.values('projname','appsystem')

        return render(request, 'cmdb/hosts.html', locals())