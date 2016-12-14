from django.shortcuts import render
from django.db.models import Q
from django.utils import timezone

from .forms import *
from .constants import *
from crm.models import Person
from registration.models import *
from registration.forms import ConferenceSelectForm


def index(request):
    """ renders base delegate/index.html page """
    new_delegate_form = NewDelegateForm()
    company_select_form = CompanySelectForm()
    assistant_form = AssistantForm()
    conference_select_form = ConferenceSelectForm()
    reg_details_form = RegDetailsForm()
    current_registration = None
    conference = None
    conference_options = None  # Remove when form working
    registrant = None
    company = None
    assistant = None
    crm_match = None
    crm_match_list = None
    options_form = None
    if request.method == 'POST':
        conf_id = request.POST['conf_id']
        conference = Event.objects.get(pk=conf_id)
        conference_options = conference.eventoptions_set.all()
        options_form = OptionsForm(conference)
        crm_id = request.POST['crm_id']
        registrant_id = request.POST['registrant_id']
        conference_select_form = ConferenceSelectForm({'event': conf_id})
        if registrant_id:
            registrant = Registrants.objects.get(pk=registrant_id)
            new_delegate_form = NewDelegateForm(instance=registrant)
            company = registrant.company
            company_select_form = CompanySelectForm(instance=company)
            assistant = registrant.assistant
            if assistant:
                assistant_form = AssistantForm(instance=assistant)
            if registrant.crm_person:
                crm_match = Person.objects.get(pk=registrant.crm_person.id)
            crm_match_list = Person.objects.filter(
                Q(name__icontains=registrant.first_name) &
                Q(name__icontains=registrant.last_name),
                Q(company__icontains=registrant.company.name)
            ).order_by('company', 'name')[:100]
    context = {
        'current_registration': current_registration,
        'new_delegate_form': new_delegate_form,
        'company_select_form': company_select_form,
        'assistant_form': assistant_form,
        'conference_select_form': conference_select_form,
        'reg_details_form': reg_details_form,
        'conference': conference,
        'conference_options': conference_options,  # remove when form working
        'options_form': options_form,
        'registrant': registrant,
        'company': company,
        'company_match': company,  # TODO: Fix this on template
        ''
        'assistant': assistant,
        'crm_match': crm_match,
        'crm_match_list': crm_match_list,
        'paid_status_values': PAID_STATUS_VALUES,
        'deposit_values': DEPOSIT_STATUS_VALUES,
        'cxl_values': CXL_VALUES,
        'sponsor_values': SPONSOR_VALUES,
    }
    return render(request, 'delegate/index.html', context)


def update_crm_match_list(request):
    """ ajax call to update crm suggestions based on delegate info """
    crm_match_list = None
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        company = request.POST['company']
        crm_match_list = Person.objects.filter(
            Q(name__icontains=first_name) &
            Q(name__icontains=last_name),
            Q(company__icontains=company)
        ).order_by('company', 'name')[:100]
    context = {
        'crm_match_list': crm_match_list,
    }
    return render(request, 'delegate/addins/crm_sidebar_list.html', context)


def link_new_crm_record(request):
    """ Ajax call to link different crm record to delegate """
    crm_match = None
    if request.method == 'POST':
        crm_match = Person.objects.get(pk=request.POST['crm_match_id'])
        if request.POST['delegate_id'] != 'new':
            registrant = Registrants.objects.get(pk=request.POST['delegate_id'])
            registrant.crm_person = crm_match
            registrant.save()
    context = {
        'crm_match': crm_match,
    }
    return render(request, 'delegate/addins/crm_sidebar_selected.html', context)


def link_new_company_record(request):
    """ ajax call to link selected company record to delegate """
    company_match = None
    if request.method == 'POST':
        company_match = Company.objects.get(pk=request.POST['company_match_id'])
        if request.POST['delegate_id'] != 'new':
            registrant = Registrants.objects.get(pk=request.POST['delegate_id'])
            registrant.company = company_match
            registrant.save()
    context = {
        'company_match': company_match,
    }
    return render(request, 'delegate/addins/company_sidebar_selected.html',
                  context)


def update_tax_information(request):
    """
    ajax call to update part of delegate page showing tax info
    happens when selected conference is changed
    should only be called for new registration
    """
    conference = None
    reg_details_form = RegDetailsForm()
    if request.method == 'POST':
        conference = Event.objects.get(pk=request.POST['conf_id'])
    context = {'conference': conference,
               'reg_details_form': reg_details_form}
    return render(request, 'delegate/addins/delegate_tax_information.html',
                  context)


def update_conference_options(request):
    """ ajax call to update conference options when event is changed """
    conference_options = None
    if request.method == 'POST':
        conf_id = request.POST['conf_id']
        conference = Event.objects.get(pk=conf_id)
        conference_options = conference.eventoptions_set.all()
    context = {'conference_options': conference_options}
    return render(request, 'delegate/addins/conference_options.html', context)


def update_fx_conversion(request):
    """
    ajax call to update fx_conversion
    happens when selected conference is changed
    should only be called for new registration
    """
    conference = None
    reg_details_form = RegDetailsForm()
    if request.method == 'POST':
        conference = Event.objects.get(pk=request.POST['conf_id'])
    context = {'conference': conference,
               'reg_details_form': reg_details_form}
    return render(request, 'delegate/addins/fx_details.html', context)


def update_cxl_info(request):
    """ ajax call to update cancellation information """
    reg_details_form = RegDetailsForm()
    if request.method == 'POST':
        form_data = {'registration_status': request.POST['reg_status'],
                     'cancellation_date': timezone.now()}
        if request.POST['regdetail_id'] != 'new':
            current_reg = RegDetails.objects.get(
                pk=request.POST['regdetail_id']
            )
            form_data['cancellation_date'] = current_reg.cancellation_date
            reg_details_form = RegDetailsForm(form_data, instance=current_reg)
        else:
            reg_details_form = RegDetailsForm(form_data)
    context = {
        'reg_details_form': reg_details_form,
        'cxl_values': CXL_VALUES,
    }
    return render(request, 'delegate/addins/cancellation_details.html',
                  context)


def update_payment_details(request):
    """ ajax call to update payment details """
    reg_details_form = RegDetailsForm()
    if request.method == 'POST':
        form_data = {'registration_status': request.POST['reg_status'],
                     'payment_method': None,
                     'deposit_method': None}
        if request.POST['reg_status'] in DEPOSIT_STATUS_VALUES:
            form_data['deposit_date'] = timezone.now()
        if request.POST['reg_status'] in PAID_STATUS_VALUES:
            form_data['payment_date'] = timezone.now()
        if request.POST['regdetail_id'] != 'new':
            current_reg = RegDetails.objects.get(
                pk=request.POST['regdetail_id']
            )
            form_data['sponsorship_description'] = \
                current_reg.sponsorship_description
            form_data['deposit_amount'] = current_reg.deposit_amount
            form_data['deposit_date'] = current_reg.deposit_date
            form_data['deposit_method'] = current_reg.deposit_method
            form_data['payment_date'] = current_reg.payment_date
            form_data['payment_method'] = current_reg.payment_method
            print('\n\n\n')
            print(current_reg.payment_method)
            print('\n\n\n')
            reg_details_from = RegDetailsForm(form_data, instance=current_reg)
        else:
            reg_details_form = RegDetailsForm(form_data)
    context = {
        'reg_details_form': reg_details_form,
        'paid_status_values': PAID_STATUS_VALUES,
        'deposit_values': DEPOSIT_STATUS_VALUES,
        'sponsor_values': SPONSOR_VALUES,
    }
    return render(request, 'delegate/addins/status_based_reg_fields.html',
                  context)


def swap_sidebar(request):
    """
    ajax call to swap content of sidebar
    """
    crm_match = None
    crm_match_list = None
    company_match_list = None
    company_match = None
    company_select_form = CompanySelectForm()
    button_action = None
    if request.method == 'POST':
        button_action = request.POST['button_action']
        if request.POST['delegate_id'] != 'new':
            registrant = Registrants.objects.get(pk=request.POST['delegate_id'])
    if button_action == 'select-crm-sidebar':
        if registrant and registrant.crm_person:
            crm_match = Person.objects.get(pk=registrant.crm_person.id)
        crm_match_list = Person.objects.filter(
            Q(name__icontains=request.POST['first_name']) &
            Q(name__icontains=request.POST['last_name']),
            Q(company__icontains=request.POST['company'])
        )
        context = {
            'crm_match': crm_match,
            'crm_match_list': crm_match_list,
            'registrant': registrant,
        }
        return render(request, 'delegate/addins/crm_sidebar.html', context)
    elif button_action == 'select-company-sidebar':
        if registrant:
            company_match = registrant.company
            company_match_list = Company.objects.filter(
                name__icontains=request.POST['company']
            )
        context = {
            'company_match': company_match,
            'company_match_list': company_match_list,
            'company_select_form': company_select_form,
            'registrant': registrant,
        }
        return render(request, 'delegate/addins/company_sidebar.html', context)
    else:
        return HttpResponse('')


def add_new_company(request):
    """ ajax call to add new company to database and link to current record """
    company_match = None
    company_match_list = None
    registrant = None
    company_select_form = CompanySelectForm()
    if request.method == 'POST':
        if request.POST['delegate_id'] != 'new':
            registrant = Registrants.objects.get(pk=request.POST['delegate_id'])
        company_select_form = CompanySelectForm(request.POST)
        if company_select_form.is_valid():
            company_match = company_select_form.save()
            if registrant:
                registrant.company = company_match
                registrant.save()
            company_select_form = CompanySelectForm()
        company_match_list = Company.objects.filter(
            name__icontains=request.POST['name']
        )
    context = {
        'company_match': company_match,
        'company_match_list': company_match_list,
        'company_select_form': company_select_form,
        'registrant': registrant,
    }
    return render(request, 'delegate/addins/company_sidebar.html', context)


def save_comany_changes(request):
    """ ajax submission to update company information when present """
    pass


def process_registration(request):
    """ form submission """
    # note that multi-select submits as 0+ versions of same fields
    # eg event-option-selection: 2
    #    event-option-selection: 12  etc
    pass
