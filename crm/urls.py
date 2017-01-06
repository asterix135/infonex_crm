from django.conf.urls import url
from . import views

app_name = 'crm'
urlpatterns = [
    # ex: /crm/
    url(r'^$', views.index, name='index'),
    # ex: /crm/1234/add_person_to_territory/
    url(r'^(?P<person_id>[0-9]+)/add_person_to_territory/$',
        views.add_person_to_territory, name='add_person_to_territory'),
    # ex /crm/1234/confirm_delete/
    url(r'^(?P<person_id>[0-9]+)/confirm_delete/$', views.confirm_delete,
        name='confirm_delete'),
    # ex /crm/create_territory/
    url(r'^create_territory/$', views.create_territory,
        name='create_territory'),
    # ex /crm/delete_person/
    url(r'^delete_person/$', views.delete_person, name='delete_person'),
    # ex /crm/detail_paginated/
    url(r'^detail_paginated/$',
        views.detail_paginated,
        name='detail_paginated'),
    # ex: /crm/flag_record/
    url(r'^flag_record/$', views.flag_record, name='flag_record'),
    # ex: /crm/flag_many_records/
    url(r'^flag_many_records/$', views.flag_many_records,
        name='flag_many_records'),
    # ex: /crm/new_person/
    url(r'^new_person/$', views.new_person, name='new_person'),
    # ex /crm/set_territory/
    url(r'^set_territory/$', views.set_territory_params, name='set_territory'),
    # ex /crm/territory/
    url(r'^territory/$', views.territory_list, name='territory'),

    ################
    # REWORKED STUFF BELOW HERE
    ################

    ################
    # MAIN PAGES
    ################
    url(r'^delete/$', views.delete, name='delete'),
    url(r'^detail/(?P<person_id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^new/$', views.new, name='new'),
    url(r'^search/$', views.search, name='search'),

    ################
    # AJAX CALLS
    ################
    url(r'^add_contact_history/$', views.add_contact_history,
        name='add_contact_history'),
    url(r'^check_for_dupes/$', views.check_for_dupes, name='check_for_dupes'),
    url(r'^delete_contact_history/$', views.delete_contact_history,
        name='delete_contact_history'),
    url(r'^get_recent_contacts/$', views.get_recent_contacts,
        name='get_recent_contacts'),
    url(r'^save_category_changes/$', views.save_category_changes,
        name='save_category_changes'),
    url(r'^save_person_details/$', views.save_person_details,
        name='save_person_details'),
    url(r'^suggest_company/$', views.suggest_company, name='suggest_company'),

    ################
    # TO BE DELETED
    ################
    # ex: /crm/1234/
    url(r'^(?P<person_id>[0-9]+)/$', views.detail_old, name='detail_old'),

]
