from django.conf.urls import url
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import path

from . import views

app_name = 'home'
urlpatterns = [
    url(r'^contact_chart/$', views.recent_contact_chart, name='contact_chart'),

    path(
        'sales_sheet/',
        login_required(views.SalesSheetView.as_view()),
        name='sales_sheet'
    ),

    url(r'^$', login_required(views.Index.as_view()), name='index'),
]
