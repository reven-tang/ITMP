from .. import models
from django import template
from django.db.models import Q

# Create your views here.

# 项目/应用
register = template.Library()

@register.simple_tag
def get_projs():
    return models.ProjectInfo.objects.values('projname').distinct()

@register.simple_tag
def get_apps():
    return models.ProjectInfo.objects.values('projname', 'appsystem')

# 统计数据
@register.simple_tag
def get_win_statistics():
    return models.DeviceInfo.objects.filter(ostype__icontains='win').count()

@register.simple_tag
def get_unix_statistics():
    return models.DeviceInfo.objects.filter(
        Q(ostype__icontains='linux') | Q(ostype__icontains='centos')).count()

@register.simple_tag
def get_app_statistics():
    return models.ProjectInfo.objects.values('appsystem').distinct().count()

@register.simple_tag
def get_soft_statistics():
    return models.SoftwareInfo.objects.values('sname').distinct().count()