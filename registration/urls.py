from django.conf.urls import url
from . import views

app_name = 'registration'

urlpatterns = [
    # BASE URLS
    url(r'^$', views.index, name='index'),
    url(r'^conference/$', views.add_edit_conference,
        name='conference'),
    url(r'^new_delegate_search/$', views.new_delegate_search,
        name='new_delegate_search'),
    url(r'^reports/$', views.reports, name="reports"),

    # AJAX Calls
    url(r'^add_event_option/$', views.add_event_option,
        name='add_event_option'),
    url(r'^add_venue/$', views.add_venue, name='add_venue'),
    url(r'^delete_event_option/$', views.delete_event_option,
        name='delete_event_option'),
    url(r'^delete_temp_conf/$', views.delete_temp_conf,
        name='delete_temp_conf'),
    url(r'^delete_venue/$', views.delete_venue, name='delete_venue'),
    url(r'^edit_venue/$', views.edit_venue, name='edit_venue'),
    url(r'^filter_venue/$', views.filter_venue, name='filter_venue'),
    url(r'^get_registration_history/$', views.get_registration_history,
        name='get_registration_history'),
    url(r'^save_conference_changes/$', views.save_conference_changes,
        name='save_conference_changes'),
    url(r'^search_dels/$', views.search_dels, name='search_dels'),
    url(r'^select_conference/$', views.select_conference_to_edit,
        name='select_conference'),
    url(r'^unfilter_venue/$', views.unfilter_venue, name='unfilter_venue'),
    url(r'^update_conference_choices/$', views.update_conference_choices,
        name='update_conference_choices'),
    url(r'^update_venue_choices/$', views.update_venue_choices,
        name='update_venue_choices'),

    # Graphics & DOCUMENTS
    url(r'^get_delegate_list/$', views.get_delegate_list,
        name='get_delegate_list'),
    url(r'^get_no_name_list/$', views.get_no_name_list,
        name='get_no_name_list'),
    url(r'^get_onsite_list/$', views.get_onsite_list, name='get_onsite_list'),
    url(r'^get_phone_list/$', views.get_phone_list, name='get_phone_list'),
    url(r'^get_registration_list/$', views.get_registration_list,
        name='get_registration_list'),
    url(r'^get_sign_in_sheet/$', views.get_sign_in_sheet,
        name='get_sign_in_sheet'),
    url(r'^get_unpaid_list/$', views.get_unpaid_list, name='get_unpaid_list'),

]
