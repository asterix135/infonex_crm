from django.conf.urls import url
from . import views

app_name = 'crm'
urlpatterns = [
    # ex: /crm/1234/add_person_to_territory/
    url(r'^(?P<person_id>[0-9]+)/add_person_to_territory/$',
        views.add_person_to_territory, name='add_person_to_territory'),
    # ex /crm/create_territory/
    url(r'^create_territory/$', views.create_territory,
        name='create_territory'),
    # ex /crm/detail_paginated/
    url(r'^detail_paginated/$',
        views.detail_paginated,
        name='detail_paginated'),
    # ex: /crm/flag_record/
    url(r'^flag_record/$', views.flag_record, name='flag_record'),
    # ex: /crm/flag_many_records/
    url(r'^flag_many_records/$', views.flag_many_records,
        name='flag_many_records'),
    # ex /crm/set_territory/
    url(r'^set_territory/$', views.set_territory_params, name='set_territory'),
    # ex /crm/territory/

    ################
    # REWORKED STUFF BELOW HERE
    ################

    ################
    # MAIN PAGES
    ################
    url(r'^$', views.index, name='index'),
    url(r'^delete/$', views.delete, name='delete'),
    url(r'^detail/(?P<person_id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^manage_territory/$', views.manage_territory,
        name='manage_territory'),
    url(r'^new/$', views.new, name='new'),
    url(r'^search/$', views.search, name='search'),
    url(r'^territory/$', views.territory, name='territory'),

    ################
    # AJAX CALLS
    ################
    url(r'^add_contact_history/$', views.add_contact_history,
        name='add_contact_history'),
    url(r'^check_for_dupes/$', views.check_for_dupes, name='check_for_dupes'),
    url(r'^create_selection_widget/$', views.create_selection_widget,
        name='create_selection_widget'),
    url(r'^check_for_user_assignment/$', views.check_for_user_assignment,
        name='check_for_user_assignment'),
    url(r'^delete_contact_history/$', views.delete_contact_history,
        name='delete_contact_history'),
    url(r'^get_recent_contacts/$', views.get_recent_contacts,
        name='get_recent_contacts'),
    url(r'^save_category_changes/$', views.save_category_changes,
        name='save_category_changes'),
    url(r'^save_person_details/$', views.save_person_details,
        name='save_person_details'),
    url(r'^suggest_company/$', views.suggest_company, name='suggest_company'),
    url(r'^update_user_assignments/$', views.update_user_assignments,
        name='update_user_assignments'),

    ################
    # TO BE DELETED
    ################
    url(r'^(?P<person_id>[0-9]+)/$', views.detail_old, name='detail_old'),
    url(r'^territory_list/$', views.territory_list, name='territory_list'),
    url(r'^new_person/$', views.new_person, name='new_person'),
    url(r'^(?P<person_id>[0-9]+)/confirm_delete/$', views.confirm_delete,
        name='confirm_delete'),
    url(r'^delete_person/$', views.delete_person, name='delete_person'),

]
