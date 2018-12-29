from django.contrib import admin
from .models import *
from django import forms as MForms
from django.forms import widgets, fields
from . import forms

# Register your models here.

# 定义ModelForm
# class SoftwareFrom(MForms.ModelForm):
#     stype = fields.ChoiceField(
#         label='软件类型',
#         choices=[('WEB', 'WEB'),('API', 'API'),('DB', 'DB'),('中间件', '中间件'),('SERVER', 'SERVER')],
#         widget=widgets.Select
#     )
#
#     class Meta:
#         model = SoftwareInfo
#         fields = '__all__'
#         # exclude = ['sid', 'customer1', 'customer2', 'customer3', 'customer4', 'customer5']


# 定义InlineModelAdmin对象,管理界面能够在与父模型相同的页面上编辑模型。这些被称为内联
class SoftwareInline(admin.TabularInline):
    model = SoftwareInfo

class RelationInline(admin.TabularInline):
    model = Relations


# 在Admin界面进行注册展示
@admin.register(DeviceInfo)
class DeviceInfoAdmin(admin.ModelAdmin):
    list_display = ['appsystem', 'devip', 'devname', 'devnamealias', 'ostype', 'devtype', 'devstatus', 'devdesc', 'location']
    list_display_links = ('appsystem', 'devip')

    # 增加了一个 “筛选” 的侧边栏
    list_filter = ['pdappsystem']

    # 定义appsystem方法,方法名和pdappsystem一致
    def appsystem(self, DeviceInfo):
        """自定义列表字段"""
        # 方法一
        # app_items = map(lambda x: x.appsystem, DeviceInfo.pdappsystem.all())
        # return ', '.join(app_items)
        # 方法二
        return [item.appsystem for item in DeviceInfo.pdappsystem.all()]
    # 自定义列标题
    appsystem.short_description = '应用系统'

    # 定义可编辑字段
    list_editable = ('devname', 'devnamealias', 'ostype', 'devtype', 'devstatus', 'devdesc', 'location')

    exclude = ['devid', 'customer1', 'customer2', 'customer3', 'customer4', 'customer5', 'customer6', 'customer7',
               'customer8']
    fieldsets = (
        (None, {
            'fields': ('devip', 'devname', 'devnamealias', 'ostype', 'devtype', 'devstatus', 'devdesc', 'location', 'pdappsystem')
        }),
        ('性能参数', {
            'classes': ('collapse',),
            'fields': (('cpusize', 'cpucorecount'), ('memsize', 'disksize')),
        }),
    )

    # 水平扩展多对多字段，并提供过滤功能
    filter_horizontal =  ('pdappsystem',)

    # 内联
    inlines = [
        SoftwareInline,
    ]

    # 定义每页显示条数
    list_per_page = 50

    # 定义搜索字段
    search_fields = ('devip',)
    # 定义默认排序字段
    ordering = ('devip',)

@admin.register(ProjectInfo)
class ProjectInfoAdmin(admin.ModelAdmin):
    list_display = ['projname', 'appsystem', 'projdesc', 'groupname', 'projcontactname', 'projcontactphone',
                    'projcontactemail', 'appcontactname', 'appcontactphone', 'appcontactemail']
    list_editable = ('projdesc', 'groupname', 'projcontactname', 'projcontactphone',
                    'projcontactemail', 'appcontactname', 'appcontactphone', 'appcontactemail')

    exclude = ['pid', 'customer1', 'customer2', 'customer3', 'customer4', 'customer5']
    fieldsets = (
        (None, {
            'fields': ('projname', 'appsystem', 'projdesc')
        }),
        ('联系人选项', {
            'classes': ('collapse',),
            'fields': ('groupname', ('projcontactname', 'projcontactphone', 'projcontactemail'),
                       ('appcontactname', 'appcontactphone', 'appcontactemail')),
        }),
    )

    # 水平扩展多对多字段，并提供过滤功能
    # filter_horizontal = ('dpdevip',)

@admin.register(SoftwareInfo)
class SoftwareInfoAdmin(admin.ModelAdmin):
    list_display = ['appsystem', 'devip', 'sname', 'stype', 'sport', 'sversion', 'spath', 'sdesc']
    list_display_links = ('appsystem', 'devip', 'sname')
    list_editable = ('stype', 'sport', 'sversion', 'spath', 'sdesc')

    exclude = ['sid', 'customer1', 'customer2', 'customer3', 'customer4', 'customer5']
    fields = ('psappsystem', 'dsdevip', 'sname', 'stype', ('sport', 'sversion'), 'spath', 'sdesc')
    form = forms.SoftwareFrom

    search_fields = ['sname']

    # 针对外键ForeignKey,将原本的下拉框展现成文本框，并附带放大镜选择添加
    raw_id_fields = ('dsdevip', 'psappsystem',)

    # 定义每页显示条数
    list_per_page = 50

    # 显示ForeignKey字段
    def devip(self, DeviceInfo):
        return DeviceInfo.dsdevip
    # 自定义列标题
    devip.short_description = '设备IP地址'

    def appsystem(self, ProjectInfo):
        return ProjectInfo.psappsystem
    # 自定义列标题
    appsystem.short_description = '应用系统'

@admin.register(Relations)
class RelationsAdmin(admin.ModelAdmin):
    list_display = ['devip', 'sname', 'upip', 'updesc', 'downip', 'downdesc']
    list_display_links = ('devip', 'sname', 'upip', 'downip')
    list_editable = ('updesc', 'downdesc')

    fields = ('drdevip', 'srsname', ('upip', 'updesc'), ('downip', 'downdesc'))

    # 针对外键ForeignKey,将原本的下拉框展现成文本框，并附带放大镜选择添加
    raw_id_fields = ('drdevip', 'srsname',)

    # 显示ForeignKey字段
    def devip(self, DeviceInfo):
        return DeviceInfo.drdevip
    # 自定义列标题
    devip.short_description = '本端设备'

    def sname(self, SoftwareInfo):
        return SoftwareInfo.srsname
    # 自定义列标题
    sname.short_description = '应用系统'