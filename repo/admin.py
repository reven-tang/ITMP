from django.contrib import admin
from .models import Post, Category, Tag
from mdeditor.widgets import MDEditorWidget
from django.db import models

# Register your models here.

# 在Admin界面注册展示
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'created_time', 'modified_time', 'author']

    # class Media:
    #     js = (
    #         '/static/js/kindeditor-4.1.11/kindeditor-all-min.js',
    #         '/static/js/kindeditor-4.1.11/lang/zh-CN.js',
    #         '/static/js/kindeditor-4.1.11/config.js',
    #     )

    # 在 admin 中使用 markdown 小组件
    formfield_overrides = {
        models.TextField: {'widget': MDEditorWidget}
    }


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'image']

class TagAdmin(admin.ModelAdmin):
    list_display = ['name']

admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)