from django.conf.urls import url
from django.contrib.auth.decorators import login_required, permission_required

from . import views

app_name = 'delegate'

urlpatterns = [
    # BASE URLS
    url(r'^$', views.index, name='index'),
    url(r'^confirmation_details/$', views.confirmation_details,
        name='confirmation_details'),
    url(r'^payment_details/$', views.ProcessPayment.as_view(),
        name='payment_details'),

    url(r'^process_registration/$',
        login_required(views.ProcessRegistration.as_view()),
        name='process_registration'),

    # AJAX CALLS
    url(r'^company_crm_modal/$',
        login_required(views.CompanyCrmModal.as_view()),
        name='company_crm_modal'),

    # url(r'^company_crm_modal/$', views.company_crm_modal,
    #     name='company_crm_modal'),
    url(r'^conf_has_regs/$', views.conf_has_regs, name='conf_has_regs'),
    url(r'^get_company_details/$', views.get_company_details,
        name='get_company_details'),
    url(r'^get_substitute_details/', views.get_substitute_details,
        name='get_substitute_details'),
    url(r'^person_is_registered/$', views.person_is_registered,
        name='person_is_registered'),
    url(r'^search_for_substitute/$', views.search_for_substitute,
        name='search_for_substitute'),
    url(r'^suggest_assistant_data/$', views.suggest_assistant_data,
        name='suggest_assistant_data'),
    url(r'^suggest_company/$', views.suggest_company, name='suggest_company'),
    url(r'^suggest_company_match/$', views.suggest_company_match,
        name='suggest_company_match'),
    url(r'^update_conference_options/$', views.update_conference_options,
        name='update_conference_options'),
    url(r'^update_cxl_info/$', views.update_cxl_info, name='update_cxl_info'),
    url(r'^update_fx_conversion/$', views.update_fx_conversion,
        name='update_fx_conversion'),
    url(r'^update_payment_details/$', views.update_payment_details,
        name='update_payment_details'),
    url(r'^update_tax_information/$', views.update_tax_information,
        name='update_tax_information'),

    # GRAPHICS/PDFS ETC
    url(r'^get_invoice/$', views.get_invoice, name='get_invoice'),
    url(r'^get_reg_note/$', views.get_reg_note, name='get_reg_note'),

    url(r'^send_conf_email/$', views.send_conf_email, name='send_conf_email'),

]
