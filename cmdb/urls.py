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

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^index', views.index, name='index'),
    # url(r'^tables', views.tables, name='tables'),
    url(r'^tables', views.TableView.as_view(), name='tables'),
    # url(r'^search', views.search, name='search'),
    url(r'^search', views.SearchView.as_view(), name='search'),
    url(r'^resadd', views.resadd, name='resadd'),
    url(r'^resedit', views.resedit, name='resedit'),
    url(r'^resdel', views.resdel, name='resdel'),
    url(r'^downloadfile', views.downloadfile, name = 'downloadfile'),
    url(r'^uploadfile', views.uploadfile, name = "uploadfile"),
    url(r'^topchart', views.topchart, name='topchart'),
    url(r'^jsondata', views.jsondata, name='jsondata'),
    url(r'^hosts', views.hosts, name='hosts'),
]
