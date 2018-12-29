# -*- coding:utf-8 -*-
from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from hosts import models as models_hosts
from . import forms
from django.db.models import Q
import os, yaml, json
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from taskdo.lib.inventory_pre_check import PreCheck
from taskdo.tasks import *
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

        # 获取登陆用户及IP地址
        action_user = request.user.username
        action_ip = ''
        try:
            if request.META['HTTP_X_FORWARDED_FOR']:
                action_ip = request.META['HTTP_X_FORWARDED_FOR']
            else:
                action_ip = request.META['REMOTE_ADDR']
        except Exception as e:
            action_ip = request.META['REMOTE_ADDR']

        # 检查表单提交的数据
        host_options = {
            "node": node,
            "username": username,
            "password": password,
            "port": port,
            "script_type": script_type,
            # ansible args
            "taskname": taskname,
            "module": module,
            "action_user": action_user,
            "action_ip": action_ip,
        }
        precheck = PreCheck(request, options=host_options)
        host_data = precheck.run()

        if host_data == 0:
            err = {'ERROR': '信息填写错误或未正确填写，请返回重新填写！'}
            return render(request, 'taskdo/detail.html', {'data': err})
        else:
            # 调用异步任务
            adhoc_task.delay(host_options, exec_bash, host_data)

        result = {'INFO': '正在执行中，您可通过点击左侧"执行历史"查看任务执行结果！'}
        return render(request, 'taskdo/detail.html', {'data': result})

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
        script_type = request.POST.get("script_type", None)

        # 获取登陆用户及IP地址
        action_user = request.user.username
        action_ip = ''
        try:
            if request.META['HTTP_X_FORWARDED_FOR']:
                action_ip = request.META['HTTP_X_FORWARDED_FOR']
            else:
                action_ip = request.META['REMOTE_ADDR']
        except Exception as e:
            action_ip = request.META['REMOTE_ADDR']

        # 检查表单提交的数据
        host_options = {
            "node": node,
            "module": module,
            "username": username,
            "password": password,
            "port": port,
            "script_type": script_type,
            # ansible args
            "taskname": taskname,
            "action_user": action_user,
            "action_ip": action_ip,
        }
        precheck = PreCheck(request, options=host_options)
        host_data = precheck.run()

        if host_data == 0 or not module:
            err = {'ERROR': '信息填写错误或未正确填写，请返回重新填写！'}
            return render(request, 'taskdo/detail.html', {'data': err})
        else:
            # 调用异步任务
            playbook_task.delay(host_options, host_data)

        result = {'INFO': '正在执行中，您可通过点击左侧"执行历史"查看任务执行结果！'}
        return render(request, 'taskdo/detail.html', {'data': result})

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