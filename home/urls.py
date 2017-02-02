from django.conf.urls import url

from . import views

app_name = 'home'
urlpatterns = [
    url(r'^contact_chart/$', views.recent_contact_chart, name='contact_chart'),
    url(r'^$', views.index, name='index'),
]
