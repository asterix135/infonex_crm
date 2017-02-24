from django.conf.urls import url
from . import views

app_name = 'delegate'

urlpatterns = [
    # BASE URLS
    url(r'^$', views.index, name='index'),
    url(r'^confirmation_details/$', views.confirmation_details,
        name='confirmation_details'),
    url(r'^process_registration/$', views.process_registration,
        name='process_registration'),

    # AJAX CALLS
    url(r'^add_new_company/$', views.add_new_company, name='add_new_company'),
    url(r'^company_crm_modal/$', views.company_crm_modal,
        name='company_crm_modal'),
    url(r'^conf_has_regs/$', views.conf_has_regs, name='conf_has_regs'),
    url(r'^link_new_company_record/$', views.link_new_company_record,
        name='link_new_company_record'),
    url(r'^link_new_crm_record/$', views.link_new_crm_record,
        name='link_new_crm_record'),
    url(r'^person_is_registered/$', views.person_is_registered,
        name='person_is_registered'),
    url(r'^update_conference_options/$', views.update_conference_options,
        name='update_conference_options'),
    url(r'^update_crm_match_list/$', views.update_crm_match_list,
        name='update_crm_match_list'),
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
