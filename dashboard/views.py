from django.views.generic import FormView, ListView, TemplateView
from django.shortcuts import render

from crm.mixins import ManagementPermissionMixin

class Index(ManagementPermissionMixin, TemplateView):
    template_name = 'dashboard/index.html'
