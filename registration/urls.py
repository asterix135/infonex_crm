from django.conf.urls import url
from . import views

app_name = 'registration'

urlpatterns = [
    # ex: /registration/
    url(r'^$', views.index, name='index'),

    url(r'^new_delegate_search/$', views.new_delegate_search,
        name='new_delegate_search'),

    url(r'^search_dels/$', views.search_dels, name='search_dels'),

    url(r'^get_registration_history/$', views.get_registration_history,
        name='get_registration_history'),

    url(r'^add_new_delegate/$', views.add_new_delegate,
        name='add_new_delegate'),

    url(r'^add_conference/$', views.add_conference,
        name='add_conference'),
]
