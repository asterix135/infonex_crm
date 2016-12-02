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
    url(r'^conference/$', views.add_edit_conference,
        name='conference'),
    url(r'^edit_venue/$', views.edit_venue, name='edit_venue'),
    url(r'^add_venue/$', views.add_venue, name='add_venue'),
    url(r'^delete_venue/$', views.delete_venue, name='delete_venue'),
    url(r'^select_conference/$', views.select_conference_to_edit,
        name='select_conference'),
    url(r'^add_event_option/$', views.add_event_option,
        name='add_event_option'),
    url(r'^delete_event_option/$', views.delete_event_option,
        name='delete_event_option'),
    url(r'^delete_temp_conf/$', views.delete_temp_conf,
        name='delete_temp_conf'),
    url(r'^save_conference_changes/$', views.save_conference_changes,
        name='save_conference_changes'),
    url(r'^filter_venue/$', views.filter_venue, name='filter_venue'),
    url(r'^unfilter_venue/$', views.unfilter_venue, name='unfilter_venue'),
]
