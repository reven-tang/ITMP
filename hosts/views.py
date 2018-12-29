from django.shortcuts import render
from django.http import HttpResponse
from . import models
from django.db.models import Q
import json
import logging
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.

class HostView(LoginRequiredMixin, ListView):
    login_url = '/users/login/'
    model = models.HostsInfo
    template_name = 'hosts/hosts.html'
    context_object_name = 'page_data'

    paginate_by = 20


class SearchView(HostView):
    def get_queryset(self):
        q = self.request.GET.get('text')
        return super(SearchView, self).get_queryset().filter(Q(hostname__icontains=q) | Q(system_ver__icontains=q)
                                                             | Q(mathine_type__icontains=q) | Q(ip__icontains=q))

    def get_context_data(self, **kwargs):
        context = super(SearchView, self).get_context_data(**kwargs)
        q = self.request.GET.get('q')
        if not q:
            context['error_msg'] = '请输入关键词!'

        return context
