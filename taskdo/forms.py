from .models import *
from django.forms import widgets, fields
from django import forms

# 上传文件
class UploadFileForm(forms.Form):
    file  = forms.FileField()

# 定义ModelForm类
class ModuleConfForm(forms.ModelForm):
    class Meta:
        model = ModuleConf
        fields = '__all__'