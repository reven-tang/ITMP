"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from . import views
from django.conf.urls.static import static
from django.conf import settings
from mysite.utils.uploadfile import upload_file

app_name = 'taskdo'
urlpatterns = [
    url(r'^$', views.taskdo, name='taskdo'),
    url(r'^deploy', views.deploy, name='deploy'),
    url(r'^adhoc', views.adhoc, name='adhoc'),
    url(r'^playbook', views.playbook, name='playbook'),
    url(r'^history', views.HistoryView.as_view(), name='history'),
    url(r'^exec_result', views.exec_result, name='exec_result'),
    url(r'^search', views.SearchView.as_view(), name='search'),
    url(r'^addmc', views.addmc, name='addmc'),
    url(r'^editmc', views.editmc, name='editmc'),
    url(r'^lookmc', views.lookmc, name='lookmc'),
    url(r'^uploadfile/(?P<dir_name>[^/]+)$', upload_file, name='upload_image'),
    url(r'^upload$', views.upload, name='upload'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)