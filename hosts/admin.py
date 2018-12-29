from django.contrib import admin
from .models import *

# Register your models here.

# 在Admin界面进行注册展示
@admin.register(HostsInfo)
class HostsInfoAdmin(admin.ModelAdmin):
    list_display = ['sn', 'ip', 'hostname', 'system_ver', 'mathine_type', 'sn_key', 'host_type']