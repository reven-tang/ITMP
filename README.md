ITMP 管理平台
===
[TOC]

## 简介
这是一个使用Python + Django + ansible开发的IT管理平台，功能包括资产管理、业务拓扑、主机发现、执行任务、WebSSH管理、监控API以及知识库与一体的IT管理系统；

欢迎大家测试使用，有问题可反馈，一起交流。

## 声明

本项目基于何全老师开发的ansible api和webssh模块进行构建，使用时可参考何全老师的项目[AutoOps](https://github.com/hequan2017/autoops/)中的License；

再次感谢何全老师！

## 环境

前端模块：

- suit-v2

后端：

- Python 3.6.5
- Django 2.0.8
- Ansible 2.4.2
- Celery 3.1.26

运行环境：

- CentoOS 7

数据库：

- Mysql

中间件：

- Redis-Server

## 部署：

1，克隆代码
```
git clone https://github.com/reven-tang/Django_ITMP.git
```

2，修改 mysite/settings.py
```
# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'mysite_db',    # 数据库名称
        'USER': 'username',     # 用户名
        'PASSWORD': 'password', # 密码
        'HOST': '127.0.0.1',    # 数据库地址
        'PORT': '3306',         # 端口
        'OPTIONS': {},
        'init_command': 'SET storage_engine=INNODB,'
                        'SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED, autocommit=1, names "utf8";',
    }
}


# Email settings smtp/pop3
EMAIL_USE_TLS = False
EMAIL_HOST = "smtp.163.com"             # 邮箱服务器
# EMAIL_PORT = 25                       # 端口
EMAIL_HOST_USER = "example@163.com"     # 用户
EMAIL_HOST_PASSWORD = "pwssword"        # 密码
EMAIL_SUBJECT_PREFIX = u"[邮件]"


#########################################################
#  celery settings
# celery中间人 redis://redis服务所在的ip地址:端口/数据库号
BROKER_URL = 'redis://127.0.0.1:6379/0'
# celery结果返回，可用于跟踪结果
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'
# celery内容等消息的格式设置
CELERY_ACCEPT_CONTENT = ['application/json', ]
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
# celery时区设置，使用settings中TIME_ZONE同样的时区
CELERY_TIMEZONE = TIME_ZONE
#########################################################

#########################################################
#  django-channels配置,配置channels路由和通道后端
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/2')],
        },
    },
}

# 配置ASGI路由的路径
ASGI_APPLICATION = "wssh.routing.application"
#########################################################
```

3，安装依赖包
```
pip3   install -r   requirements.txt
pip3 install https://github.com/darklow/django-suit/tarball/v2
```

4，安装Ansible、Mysql和Redis，略过...

5，同步数据库
```
cd mysite
python manage.py makemigrations
python manage.py migrate
```

6，创建超级用户：
```
cd mysite
python manage.py createsuperuser
```

7，启动

```
cd mysite
python3   manage.py runserver 0.0.0.0:80  或 nohup python3 manage.py runserver 0.0.0.0:80 >> logs/mysite.log 2>&1 &

celery -A mysite worker -l info  或  nohup celery -A mysite worker -l info >> logs/celery.log 2>&1 &
```

## 截图

**登陆**

![登陆](https://github.com/reven-tang/Django_ITMP/blob/master/photo/login.jpg "登陆")

**资产**

![资产](https://github.com/reven-tang/Django_ITMP/blob/master/photo/cmdb1.jpg "资产")

![资产](https://github.com/reven-tang/Django_ITMP/blob/master/photo/cmdb2.jpg "资产")

**业务拓扑**

![拓扑](https://github.com/reven-tang/Django_ITMP/blob/master/photo/top.jpg "拓扑")

![拓扑](https://github.com/reven-tang/Django_ITMP/blob/master/photo/top2.jpg "拓扑")

**主机**

![主机](https://github.com/reven-tang/Django_ITMP/blob/master/photo/host.jpg "主机")

**远程命令**

![远程命令](https://github.com/reven-tang/Django_ITMP/blob/master/photo/task1.jpg "远程命令")

**模块配置及部署**

![模块配置及部署](https://github.com/reven-tang/Django_ITMP/blob/master/photo/task2.jpg "模块配置及部署")

![模块配置及部署](https://github.com/reven-tang/Django_ITMP/blob/master/photo/task3.jpg "模块配置及部署")

**执行历史及日志审计**

![执行历史](https://github.com/reven-tang/Django_ITMP/blob/master/photo/task4.jpg "执行历史")

**Web SSH**

![Web SSH](https://github.com/reven-tang/Django_ITMP/blob/master/photo/webssh.jpg "Web SSH")

**监控**

![监控](https://github.com/reven-tang/Django_ITMP/blob/master/photo/api.jpg "监控")

![监控](https://github.com/reven-tang/Django_ITMP/blob/master/photo/chart.jpg "监控")

**知识库**

![知识库](https://github.com/reven-tang/Django_ITMP/blob/master/photo/zhishi.jpg "知识库")

## 贡献者

**1.0**
- Reven


