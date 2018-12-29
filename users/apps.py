from django.apps import AppConfig
from suit.apps import DjangoSuitConfig

class UsersConfig(AppConfig):
    name = 'users'
    verbose_name = '用户管理'

class SuitConfig(DjangoSuitConfig):
    layout = 'vertical'
    # layout这个参数决定你的网页是初始样式是垂直样式还是水平样式，可选参数为‘horizontal’或‘vertical’
