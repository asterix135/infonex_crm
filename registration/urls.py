from django.conf.urls import url
from django.contrib.auth.decorators import login_required, permission_required

from . import views

app_name = 'registration'

urlpatterns = [
    # BASE URLS
    url(r'^$', views.index, name='index'),
    url(r'^conference/$', views.add_edit_conference,
        name='conference'),
    url(r'^mass_mail$', views.mass_mail, name='mass_mail'),
    url(r'^new_delegate_search/$', views.new_delegate_search,
        name='new_delegate_search'),
    url(r'^send_mass_email/$', views.process_mass_email,
        name='send_mass_email'),

    # AJAX Calls

    url(r'^update_event_option/$',
        login_required(views.UpdateEventOptions.as_view()),
        name='update_event_option'),


    url(r'^add_event_option/$', views.add_event_option,
        name='add_event_option'),
    url(r'^add_venue/$', views.add_venue, name='add_venue'),
    url(r'^delete_temp_conf/$', views.delete_temp_conf,
        name='delete_temp_conf'),
    url(r'^delete_venue/$', views.delete_venue, name='delete_venue'),
    url(r'^edit_venue/$', views.edit_venue, name='edit_venue'),
    url(r'^filter_venue/$', views.filter_venue, name='filter_venue'),
    url(r'^find_reg/$', views.find_reg, name='find_reg'),
    url(r'^get_registration_history/$', views.get_registration_history,
        name='get_registration_history'),
    url(r'^index_panel/$', views.index_panel, name='index_panel'),
    url(r'^mass_mail_details/$', views.mass_mail_details,
        name='mass_mail_details'),
    url(r'^save_conference_changes/$', views.save_conference_changes,
        name='save_conference_changes'),
    url(r'^search_dels/$', views.search_dels, name='search_dels'),
    url(r'^select_conference/$', views.select_conference_to_edit,
        name='select_conference'),
    url(r'^suggest_first_name/$', views.suggest_first_name,
        name='suggest_first_name'),
    url(r'^suggest_last_name/$', views.suggest_last_name,
        name='suggest_last_name'),
    url(r'^unfilter_venue/$', views.unfilter_venue, name='unfilter_venue'),
    url(r'^update_conference_choices/$', views.update_conference_choices,
        name='update_conference_choices'),
    url(r'^update_venue_choices/$', views.update_venue_choices,
        name='update_venue_choices'),

    # Graphics & DOCUMENTS
    url(r'^event_revenue/$', views.event_revenue,
        name='event_revenue'),
    url(r'^get_admin_reports/$', views.get_admin_reports,
        name='get_admin_reports'),
    url(r'^get_sales_reports/$', views.get_sales_reports,
        name='get_sales_reports'),
]
