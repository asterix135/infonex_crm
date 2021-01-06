from django.conf.urls import url
from django.contrib.auth.decorators import login_required, permission_required

from . import views

app_name = 'crm'
urlpatterns = [
    ################
    # MAIN PAGES
    ################
    url(r'^$', views.index, name='index'),

    url(r'^delete/$', views.delete, name='delete'),

    url(r'^detail/(?P<pk>[0-9]+)/$',
        login_required(views.Detail.as_view()),
        name='detail'),

    url(r'^manage_territory/$',
        login_required(views.ManageTerritory.as_view()),
        name='manage_territory'),

    url(r'^new/$', views.new, name='new'),

    url(r'^search/$',
        login_required(views.Search.as_view()),
        name='search'),

    url(r'^territory/$',
        login_required(views.Territory.as_view()),
        name='territory'),

    ################
    # AJAX CALLS
    ################
    url(r'^add_contact_history/$', views.add_contact_history,
        name='add_contact_history'),
    url(r'^add_master_list_select/$', views.add_master_list_select,
        name='add_master_list_select'),
    url(r'^add_personal_list_select/$', views.add_personal_list_select,
        name='add_personal_list_select'),

    url(r'^change_flag/$',
        login_required(views.ChangeFlag.as_view()),
        name='change_flag'),

    url(r'^check_for_dupes/$', views.check_for_dupes, name='check_for_dupes'),

    url(r'^create_selection_widget/(?P<pk>[0-9]+)/$',
        login_required(views.CreateSelectionWidget.as_view()),
        name='create_selection_widget'),

    url(r'^delete_contact_history/$', views.delete_contact_history,
        name='delete_contact_history'),
    url(r'^delete_master_list_select/$', views.delete_master_list_select,
        name='delete_master_list_select'),
    url(r'^delete_personal_list_select/$', views.delete_personal_list_select,
        name='delete_personal_list_select'),

    url(r'^export_list_selects/(?P<pk>[0-9]+)/$',
        login_required(views.ExportListSelects.as_view()),
        name='export_list_selects'),

    url(r'^get_recent_contacts/$', views.get_recent_contacts,
        name='get_recent_contacts'),

    url(r'^group_flag_update/$',
        login_required(views.GroupFlagUpdate.as_view()),
        name='group_flag_update'),

    url(r'^load_staff_category_selects/$',
        login_required(views.LoadStaffCategorySelects.as_view()),
        name='load_staff_category_selects'),
    url(r'^load_staff_member_selects/$',
        login_required(views.LoadStaffMemberSelects.as_view()),
        name='load_staff_member_selects'),
    url(r'^reg_options/$',
        login_required(views.RegOptions.as_view()),
        name='reg_options'),

    url(r'^save_category_changes/$', views.save_category_changes,
        name='save_category_changes'),
    url(r'^save_person_details/$', views.save_person_details,
        name='save_person_details'),

    url(r'^select_active_conference/$',
        login_required(views.SelectActiveConference.as_view()),
        name='select_active_conference'),
    url(r'^submit_registration/$',
        login_required(views.SubmitRegistration.as_view()),
        name='submit_registration'),

    url(r'^suggest_company/$', views.suggest_company, name='suggest_company'),
    url(r'^suggest_dept/$', views.suggest_dept, name='suggest_dept'),
    url(r'^suggest_industry/$', views.suggest_industry,
        name='suggest_industry'),
    url(r'^toggle_person_in_territory/$', views.toggle_person_in_territory,
        name='toggle_person_in_territory'),
    url(r'^toggle_territory_filter/$', views.toggle_territory_filter,
        name='toggle_territory_filter'),
    url(r'^update_user_assignments/$', views.update_user_assignments,
        name='update_user_assignments'),

    ################
    # GRAPHICS
    ################
    url(r'^call_report/$', views.call_report, name='call_report'),

    url(r'^registration_form/(?P<pk>[0-9]+)/$',
        login_required(views.RegistrationForm.as_view()),
        name='registration_form'),

]
