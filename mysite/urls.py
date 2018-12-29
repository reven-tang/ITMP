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
from django.contrib import admin
from django.urls import path
from django.conf.urls import include, url
from django.conf import settings
from django.views import static as vstatic
from django.conf.urls.static import static
from .utils.upload import upload_image

# API
from rest_framework.routers import DefaultRouter
from api import views
# Create a router and register our viewsets with it.
# viewsets可以通过简单地使用路由器类注册视图来自动生成API的URL conf
router = DefaultRouter()
router.register(r'Details', views.MonitorViewSet)

urlpatterns = [
    url(r'^admin/upload/(?P<dir_name>[^/]+)$', upload_image, name='upload_image'),
    url(r'^uploads/(?P<path>.*)$', vstatic.serve, {'document_root': settings.MEDIA_ROOT, }),
    path('admin/', admin.site.urls),
    url(r'^$', include('cmdb.urls')),
    url(r'^index', include('cmdb.urls')),
    url(r'^cmdb/', include('cmdb.urls')),
    url(r'^repo/', include('repo.urls')),
    url(r'^taskdo/', include('taskdo.urls')),
    url(r'^hosts/', include('hosts.urls')),
    url(r'^users/', include('users.urls')),
    url(r'^users/', include('django.contrib.auth.urls')),
    url(r'mdeditor/', include('mdeditor.urls')),
    url(r'^wssh/', include('wssh.urls')),

    # API
    url(r'^api', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    url(r'^chart/', include('api.urls')),
]
if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
