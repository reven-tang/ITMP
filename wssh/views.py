from django.shortcuts import redirect, render
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from hosts import models as models_hosts
from wssh.lib.inventory_pre_check import PreCheck
import json
# Create your views here.

@login_required(login_url='/users/login/')
def wssh(request):
    if request.method == "GET":
        hosts = models_hosts.HostsInfo.objects.all()
        return render(request, 'wssh/wssh.html', locals())
    else:
        raise Http404

@login_required(login_url='/users/login/')
def terminal(request):
    if request.method == "POST":
        node = request.POST.getlist('node', None)
        port = request.POST.get('port', None)
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)

        # 检查表单提交的数据
        host_options = {
            "node": node,
            "username": username,
            "password": password,
            "port": port
        }
        precheck = PreCheck(request, options=host_options)
        host_data = precheck.run()

        if host_data == 0:
            err = {'ERROR': '信息填写错误或未正确填写，请返回重新填写！'}
            return render(request, 'taskdo/detail.html', {'data': err})
        else:
            jsonData = json.dumps(host_data[0])
            return HttpResponse(jsonData)