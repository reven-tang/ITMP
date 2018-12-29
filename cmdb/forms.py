from .models import *
from django.forms import widgets, fields
from django import forms

# CSV上传导入
class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file  = forms.FileField()


# 定义ModelForm类
class DeviceForm(forms.ModelForm):
    # 将多对多字段展现为多选框
    # 方法一：
    # pdappsystem = forms.ModelMultipleChoiceField(
    #     queryset=ProjectInfo.objects.all(),
    #     widget=forms.CheckboxSelectMultiple())

    # 方法二：
    # def __init__(self, *args, **kwargs):
    #     super(DeviceForm, self).__init__(*args, **kwargs)
    #
    #     self.fields["pdappsystem"].widget = widgets.CheckboxSelectMultiple()
    #     self.fields["pdappsystem"].queryset = ProjectInfo.objects.all()

    class Meta:
        model = DeviceInfo
        fields = '__all__'
        exclude = ['devid', 'customer1', 'customer2', 'customer3', 'customer4', 'customer5', 'customer6' ,'customer7', 'customer8']

class ProjectFrom(forms.ModelForm):
    # 将多对多字段展现为多选框
    # dpdevip = forms.ModelMultipleChoiceField(
    #     queryset=DeviceInfo.objects.all(),
    #     widget=forms.CheckboxSelectMultiple())

    class Meta:
        model = ProjectInfo
        fields = '__all__'
        exclude = ['pid', 'customer1', 'customer2', 'customer3', 'customer4', 'customer5']

class SoftwareFrom(forms.ModelForm):
    stype = fields.ChoiceField(
        label='软件类型',
        choices=[(None, '---------'), ('WEB', 'WEB'),('API', 'API'),('DB', 'DB'),('中间件', '中间件'),('SERVER', 'SERVER')],
        widget=widgets.Select
    )

    class Meta:
        model = SoftwareInfo
        fields = '__all__'
        exclude = ['sid', 'customer1', 'customer2', 'customer3', 'customer4', 'customer5']

class RelationsFrom(forms.ModelForm):

    class Meta:
        model = Relations
        fields = '__all__'
        exclude = ['rid']