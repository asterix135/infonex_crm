from django.conf.urls import url
from django.contrib.auth.decorators import login_required, permission_required

from . import views

app_name = 'marketing'
urlpatterns = [
    url(r'^$', login_required(views.Index.as_view()), name='index'),
]
