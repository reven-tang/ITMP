from django.apps import AppConfig

# 在Admin界面将CMDB应用显示为中文定义
class CmdbConfig(AppConfig):
    name = 'cmdb'
    verbose_name = '资产管理'
