from django.contrib import admin
from .models import *

# Register your models here.

# 在Admin界面进行注册展示
@admin.register(ModuleConf)
class ModuleConfAdmin(admin.ModelAdmin):
    list_display = ['module_name', 'module_path']

