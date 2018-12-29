from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

from . import models
from rest_framework import viewsets
from .serializers import MonitorSerializer
from django.contrib.auth.decorators import login_required
import json
from django.db.models import Q


class MonitorViewSet(viewsets.ModelViewSet):
    """
    允许用户查看或编辑的API路径。
    """
    queryset = models.MonitorInfo.objects.all().order_by('-id')[:10]
    serializer_class = MonitorSerializer

    '''
    curl:
        -H/--header <line> : 自定义头信息传递给服务器
        -u/--user <user[:password]> : 设置服务器的用户和密码
        -d/--data <data> : HTTP POST方式传送数据
        -I/--head : -I/--head
            例如：curl -I -u 'admin:Admin&123.' http://192.168.122.17/apiDetails/
            HTTP/1.1 200 OK
            Content-Type: application/json
            Vary: Accept, Cookie
            Allow: GET, POST, HEAD, OPTIONS
            X-Frame-Options: SAMEORIGIN
            Content-Length: 400
        -X/--request <command> : 指定什么命令，如果是POST方法必须把数据和网址分开，curl就要用到--data参数
            例如： 
            curl -X GET -u 'admin:Admin&123.' http://192.168.122.17/apiDetails/
            curl -H 'Accept: application/json; indent=4' -u 'admin:Admin&123.' -X POST --data 'ipaddr=192.168.0.38&hostname=MICROSO-7CC9K12&platform=Windows-10-10.0.15063&cpucorecount=4&memsize=16&index=MemUtilization&value=22.6' http://192.168.122.17/apiDetails/
            curl -u 'admin:Admin&123.' -X POST --data 'ipaddr=192.168.0.38&hostname=MICROSO-7CC9K12&platform=Windows-10-10.0.15063&cpucorecount=4&memsize=16&index=MemUtilization&value=22.6' http://192.168.122.17/apiDetails/
            curl -X DELETE -u 'admin:Admin&123.' http://192.168.122.17/apiDetails/14/
    GET:
        curl -H 'Accept: application/json; indent=4' -u 'admin:Admin&123.' http://192.168.122.17/aiDetails/
    POST:        
        curl -H 'Accept: application/json; indent=4' -u 'admin:Admin&123.' -d 'ipaddr=192.168.0.38&hostname=MICROSO-7CC9K12&platform=Windows-10-10.0.15063&cpucorecount=4&memsize=16&index=MemUtilization&value=22.6' http://192.168.122.17/apiDetails/
    
    '''

# 图表
@login_required(login_url='/users/login/')
def chart(request):
    ipaddr = models.MonitorInfo.objects.all().values_list('ipaddr', flat=True).distinct()
    kpi = models.MonitorInfo.objects.all().values_list('kpi', flat=True).distinct()
    return render(request, 'chart/chart.html', locals())

def jsondata(request):
    if request.method == "GET":
        # 构造xdata,ydata数据
        ip = '192.168.122.17'
        xdata = list(models.MonitorInfo.objects.filter(Q(kpi = 'CpuUtilization') & Q(ipaddr=ip)).values_list('mtime', flat=True))[0-288:]
        cpu_data = list(models.MonitorInfo.objects.filter(Q(kpi = 'CpuUtilization') & Q(ipaddr=ip)).values_list('values', flat=True))[0-288:]
        mem_data = list(models.MonitorInfo.objects.filter(Q(kpi = 'MemUtilization') & Q(ipaddr=ip)).values_list('values', flat=True))[0-288:]
        disk_data = list(models.MonitorInfo.objects.filter(Q(kpi__icontains = 'DiskUtilization') & Q(ipaddr=ip)).values_list('kpi', flat=True).distinct())

        disk_list = []
        for i in disk_data:
            tmp = {
                str(i): list(models.MonitorInfo.objects.filter(Q(kpi=str(i)) & Q(ipaddr=ip)).values_list('values', flat=True))[0-288:]
            }
            disk_list.append(tmp)

        data = {
            'x': xdata,
            'cpuData': cpu_data,
            'memData': mem_data,
            'diskData': disk_list,
            'diskNum': len(disk_data)
        }

        jsonData = json.dumps(data)
        return HttpResponse(jsonData)

    elif request.method == "POST":
        ipaddr = str(request.POST.get('ipaddr', None))
        kpi = str(request.POST.get('kpi', None))

        # 构造xdata,ydata数据
        xdata = list(models.MonitorInfo.objects.filter(Q(kpi = kpi) & Q(ipaddr=ipaddr)).values_list('mtime', flat=True))[0-288:]
        ydata = list(models.MonitorInfo.objects.filter(Q(kpi = kpi) & Q(ipaddr=ipaddr)).values_list('values', flat=True))[0-288:]

        data = {
            'x': xdata,
            'kpiname': kpi,
            'y': ydata
        }

        jsonData = json.dumps(data)
        return HttpResponse(jsonData)

