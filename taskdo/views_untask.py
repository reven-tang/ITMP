# -*- coding:utf-8 -*-
from django.shortcuts import render, redirect
from django.http import Http404
from taskdo.utils.runner import AdHocRunner, CommandRunner, PlayBookRunner
from taskdo.utils.inventory import BaseInventory
from mysite.utils.insertdb_history import InsertExecHistory
from hosts import models as models_hosts
from . import models, forms
from django.db.models import Q
import os, json, yaml, datetime
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from hosts.lib.utils import prpcrypt
from taskdo.lib.inventory_pre_check import PreCheck
# Create your views here.

import logging
logger = logging.getLogger('taskdo.view')

# adhoc页面
@login_required(login_url='/users/login/')
def taskdo(request):
    if request.method == "GET":
        hosts = models_hosts.HostsInfo.objects.all()
        return render(request, 'taskdo/taskdo.html', locals())
    else:
        raise Http404


# 执行adhoc命令并记录到执行历史数据库
@login_required(login_url='/users/login/')
def adhoc(request):
    if request.method == "POST":
        taskname = request.POST.get('taskname', None)
        node = request.POST.getlist('node',None)
        exec_bash = request.POST.get("exec_bash", None)
        module = request.POST.get("module", None)
        username = request.POST.get("user", None)
        password = request.POST.get("pass", None)
        port = request.POST.get("port", None)
        script_type = request.POST.get("script_type", None)

        # 检查表单提交的数据
        host_options = {
            "node": node,
            "module": module,
            "username": username,
            "password": password,
            "port": port,
            "script_type": script_type
        }
        precheck = PreCheck(request, options=host_options)
        host_data = precheck.run()
        if host_data == 0:
            err = {'ERROR': '信息填写错误或未正确填写，请返回重新填写！'}
            return render(request, 'taskdo/detail.html', {'data': err})

        inventory = BaseInventory(host_data)
        exec_starttime = datetime.datetime.now()
        if module:
            pass
        else:
            if int(script_type) == 0:
                module = 'shell'
            else:
                module = 'powershell'

        if port:
            pass
        else:
            if int(script_type) == 0:
                port = '22'
            else:
                port = '5986'

        if username:
            pass
        else:
            username = ''

        # 执行命令
        # exec_bash = exec_bash.replace('\r\n', ' ; ')
        if len(exec_bash.split('\r\n')) == 0 and module != 'setup':
            runner = CommandRunner(inventory)

            res = runner.execute(exec_bash, 'all', module)
            results = res.results_raw
            # result_stdout = res.results_command['Server']['stdout']
        else:
            runner = AdHocRunner(inventory)

            print(runner)

            run_cmds = []
            for i, line in enumerate(exec_bash.split('\r\n')):
                if len(line.strip()) > 0:
                    run_cmds.append(
                        {"action": {"module": module,
                                    "args": line
                                    },
                         "name": "run_cmd" + str(i + 1)
                         },
                    )

            res = runner.run(run_cmds, "all")
            results = res.results_raw

        '''
        写入数据库：执行历史信息表
        '''
        exec_state = ''
        if len(results['failed']) > 0:
            exec_state = 'failed'
        elif len(results['unreachable']) > 0:
            exec_state = 'unreachable'
        elif len(results['skipped']) > 0:
            exec_state = 'skipped'
        else:
            exec_state = 'ok'

        exec_bash = exec_bash.replace('\r\n', ' ; ')

        options = {
            "identifier": taskname + '_' + str(exec_starttime),
            "exec_starttime": exec_starttime,
            "action": "任务",
            "exec_type": "远程命令",
            "exec_state": exec_state,
            "exec_result": results,
            "exec_module": module,
            "exec_bash": exec_bash,
            "exec_node": node,
            "ssh_user": username,
            # "ssh_passwd": password,
            "ssh_port": port,
            # "ssh_rsa": ssh_rsa,
        }
        runner = InsertExecHistory(request, options=options)
        runner.run()

        jsonData = json.dumps(results)
        # return HttpResponse(jsonData)
        return render(request, 'taskdo/detail.html', {'data': jsonData})

# playbook页面
@login_required(login_url='/users/login/')
def deploy(request):
    if request.method == "GET":
        hosts = models_hosts.HostsInfo.objects.all()
        modules = models.ModuleConf.objects.values_list('module_name', flat=True)
        mcform = forms.ModuleConfForm()
        mcdetail = models.ModuleConf.objects.all()
        return render(request, 'taskdo/deploy.html', locals())
    else:
        raise Http404

# 添加模块
@login_required(login_url='/users/login/')
def addmc(request):
    if request.method == "GET":
        mcform = forms.ModuleConfForm()
        return render(request, 'taskdo/addmc.html', locals())
    if request.method == "POST":
        mcform = forms.ModuleConfForm(request.POST)
        module_path = request.POST.get("module_path", None)
        if os.path.exists(module_path):
            if mcform.is_valid():
                confadd = mcform.save(commit=False)
                confadd.save()
                result = {'OK': '添加模块成功！'}
                return redirect('/taskdo/deploy')
        else:
            result = {'ERROR': module_path + '文件不存在，请重新填写！'}
            return render(request, 'taskdo/detail.html', {'data': result})

# 资源模块
def editmc(request):
    id = request.GET.get('id')
    if id:
        mc_info = models.ModuleConf.objects.get(id=id)

    if request.method == "GET":
        mcform = forms.ModuleConfForm(instance=mc_info)
        return render(request, 'taskdo/editmc.html', locals())

    if request.method == "POST":
        module_name = request.POST.get("module_name", None)
        module_path = request.POST.get("module_path", None)
        mc_info = models.ModuleConf.objects.get(module_name=module_name)
        mcform = forms.ModuleConfForm(request.POST, instance=mc_info)
        if os.path.exists(module_path):
            if mcform.is_valid():
                confadd = mcform.save(commit=False)
                confadd.save()
                result = {'OK': '添加模块成功！'}
                return redirect('/taskdo/deploy')
        else:
            result = {'ERROR': module_path + '文件不存在，请重新填写！'}
            return render(request, 'taskdo/detail.html', {'data': result})


# 查看模块配置
@login_required(login_url='/users/login/')
def lookmc(request):
    if request.method == "GET":
        try:
            id = request.GET.get('id')
            module_path = str(models.ModuleConf.objects.filter(id=id).values_list('module_path', flat=True)[0])
            with open(module_path, 'r') as f:
                yml_conf = yaml.load(f.read())
                jsonData = json.dumps(yml_conf)
                # return HttpResponse(jsonData)
                return render(request, 'taskdo/detail.html', {'data': jsonData})
        except:
            err = {'ERROR': 'id无效！'}
            return render(request, 'taskdo/detail.html', {'data': err})
    if request.method == "POST":
        try:
            module = request.POST.get("module", None)
            module_path = str(
                models.ModuleConf.objects.filter(module_name=module).values_list('module_path', flat=True)[0])
            with open(module_path, 'r') as f:
                yml_conf = yaml.load(f.read())
                jsonData = json.dumps(yml_conf)
                # return HttpResponse(jsonData)
                return render(request, 'taskdo/detail.html', {'data': jsonData})
        except:
            err = {'ERROR': '信息填写错误或未正确填写，请返回重新填写！'}
            return render(request, 'taskdo/detail.html', {'data': err})


# 执行playbook命令并记录到执行历史数据库
@login_required(login_url='/users/login/')
def playbook(request):
    if request.method == "POST":
        taskname = request.POST.get('taskname', None)
        node = request.POST.getlist('node',None)
        module = request.POST.get("module", None)
        username = request.POST.get("user", None)
        password = request.POST.get("pass", None)
        port = request.POST.get("port", None)
        exec_starttime = datetime.datetime.now()

        # 处理主机信息
        host_data = []
        # 优先使用前台传过来的用户、密码、端口信息；
        # 其次，如果前台传递过来的为空或者无法登陆则使用数据库中的信息进行认证；
        # 最后使用公钥认证。
        decrypt_do = prpcrypt()
        ssh_rsa = ''
        for item in node:
            if port:
                pass
            else:
                try:
                    port = str(models_hosts.HostsInfo.objects.filter(ip=item).values_list('ssh_port', flat=True)[0])
                except:
                    port = '22'

            if module:
                module_path = str(models.ModuleConf.objects.filter(module_name=module).values_list('module_path', flat=True)[0])

            if username and password:
                pass
            else:
                try:
                    username = str(models_hosts.HostsInfo.objects.filter(ip=item).values_list('ssh_user', flat=True)[0])
                except:
                    username = ''

                try:
                    encrypt_passwd = str(models_hosts.HostsInfo.objects.filter(ip=item).values_list('ssh_passwd', flat=True)[0])
                    password = decrypt_do.decrypt(encrypt_passwd)
                except:
                    try:
                        ssh_rsa = str(models_hosts.HostsInfo.objects.filter(ip=item).values_list('ssh_rsa', flat=True)[0])
                    except:
                        password = ' '

            if password:
                host_data.append(
                    {
                        "hostname": item,
                        "ip": item,
                        "port": port,
                        "username": username,
                        "password": password,
                    },
                )
            else:
                host_data.append(
                    {
                        "hostname": item,
                        "ip": item,
                        "port": port,
                        "username": username,
                        "private_key": ssh_rsa,
                    },
                )
        if host_data:
            inventory = BaseInventory(host_data)
        else:
            err = {'ERROR': '信息填写错误或未正确填写，请返回重新填写！'}
            return render(request, 'taskdo/detail.html', {'data': err})

        # 执行playbook
        runner = PlayBookRunner(playbook_path=module_path, inventory=inventory)
        results = runner.run()

        '''
        写入数据库：执行历史信息表
        '''
        # 处理执行返回状态
        exec_state = ''
        is_failed = 0
        is_unreachable = 0
        is_skipped = 0
        is_change =  0
        is_ok = 0
        for item in node:
            if results['status'][item]['failures'] > 0:
                is_failed = 1
            elif results['status'][item]['unreachable'] > 0:
                is_unreachable = 1
            elif results['status'][item]['skipped'] > 0:
                is_skipped = 1
            elif results['status'][item]['changed'] > 0:
                is_change = 1
            else:
                is_ok = 1
        if is_failed > 0:
            exec_state = 'failed'
        elif is_unreachable > 0:
            exec_state = 'unreachable'
        elif is_skipped > 0:
            exec_state = 'skipped'
        elif is_change == 0:
            exec_state = 'unchange'
        else:
            exec_state = 'ok'

        exec_bash = exec_bash.replace('\r\n', ' ; ')

        options = {
            "identifier": taskname + '_' + str(exec_starttime),
            "exec_starttime": exec_starttime,
            "action": "任务",
            "exec_type": "模块部署",
            "exec_state": exec_state,
            "exec_result": results,
            "exec_module": module,
            "exec_bash": module_path,
            "exec_node": node,
            "ssh_user": username,
            "ssh_passwd": password,
            "ssh_port": port,
            "ssh_rsa": ssh_rsa,
        }
        runner = InsertExecHistory(request, options=options)
        runner.run()

        jsonData = json.dumps(results)
    # return HttpResponse(jsonData)
    return render(request, 'taskdo/detail.html', {'data': jsonData})


# 执行历史
class HistoryView(LoginRequiredMixin, ListView):
    login_url = '/users/login/'
    model = models.ExecHisotry
    template_name = 'taskdo/history.html'
    context_object_name = 'page_data'

    paginate_by = 20

class SearchView(HistoryView):
    def get_queryset(self):
        q = self.request.GET.get('text')
        return super(SearchView, self).get_queryset().filter(Q(identifier__icontains=q) | Q(action_user__icontains=q)
                                                             | Q(action_ip__icontains=q) | Q(exec_type__icontains=q)
                                                             | Q(exec_module__icontains=q))

    def get_context_data(self, **kwargs):
        context = super(SearchView, self).get_context_data(**kwargs)
        q = self.request.GET.get('q')
        if not q:
            context['error_msg'] = '请输入关键词!'

        return context

# 执行详情
@login_required(login_url='/users/login/')
def exec_result(request):
    if request.method == "GET":
        id = request.GET.get('id')
        results = ''
        if id:
            results = models.ExecHisotry.objects.filter(id=id).values('exec_result')
        return render(request, 'taskdo/detail.html', {'data': list(results)[0]['exec_result']})
    elif request.method == "POST":
        taskname = request.POST.get('taskname', None).strip()
        try:
            action_user = request.user.username
            results = ''
            if taskname:
                results = models.ExecHisotry.objects.filter(Q(action_user__icontains=action_user) &
                                                            Q(identifier__icontains=taskname)).order_by(
                    "-exec_starttime").values('exec_result')
            return render(request, 'taskdo/detail.html', {'data': list(results)[0]['exec_result']})
        except:
            # return HttpResponse('任务名称填写错误或未正确填写，请返回重新填写！')
            err = {'ERROR': '任务名称填写错误或未正确填写，请返回重新填写！'}
            return render(request, 'taskdo/detail.html', {'data': err})
    else:
        raise Http404

# 上传文件页面
@login_required(login_url='/users/login/')
def upload(request):
    form = forms.UploadFileForm()
    return render(request, 'taskdo/upload.html', {'form': form})