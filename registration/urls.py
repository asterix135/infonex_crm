from django.conf.urls import url
from . import views

app_name = 'registration'

urlpatterns = [
    # ex: /registration/
    url(r'^$', views.index, name='index'),
]