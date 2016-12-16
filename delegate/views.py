from django.shortcuts import render
from django.http import HttpResponse
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
    new_company_form = NewCompanyForm()
    company_match_list = None
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
    data_source = None
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
            company_match_list = Company.objects.filter(
                name__icontains=company.name
            )
            data_source = 'delegate'
        else:  # No registrant, so use CRM
            crm_match = Person.objects.get(pk=request.POST['crm_id'])
            name_tokens = crm_match.name.split()
            if len(name_tokens) == 1:
                first_name_guess = ''
                last_name_guess = name_tokens[0]
            elif len(name_tokens) > 1:
                first_name_guess = name_tokens[0]
                last_name_guess = ' '.join(name_tokens[1:])
            else:
                first_name_guess = last_name_guess = ''
            form_data = {'first_name': first_name_guess,
                         'last_name': last_name_guess,
                         'title': crm_match.title,
                         'email1': crm_match.email,
                         'phone1': crm_match.phone,
                         'contact_option': 'D',
            }
            new_delegate_form = NewDelegateForm(form_data)
            crm_match_list = Person.objects.filter(
                name__icontains=crm_match.name,
                company__icontains=crm_match.company
            )
            company_match_list = Company.objects.filter(
                name__icontains=crm_match.company
            )
            company_select_form = CompanySelectForm(
                {'name': crm_match.company}
            )
            data_source = 'crm'
    context = {
        'current_registration': current_registration,
        'new_delegate_form': new_delegate_form,
        'company_select_form': company_select_form,
        'new_company_form': new_company_form,
        'company_match_list': company_match_list,
        'assistant_form': assistant_form,
        'conference_select_form': conference_select_form,
        'reg_details_form': reg_details_form,
        'conference': conference,
        'conference_options': conference_options,  # remove when form working
        'options_form': options_form,
        'registrant': registrant,
        'company': company,
        'assistant': assistant,
        'crm_match': crm_match,
        'crm_match_list': crm_match_list,
        'paid_status_values': PAID_STATUS_VALUES,
        'deposit_values': DEPOSIT_STATUS_VALUES,
        'cxl_values': CXL_VALUES,
        'sponsor_values': SPONSOR_VALUES,
        'data_source': data_source,
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
    company = None
    if request.method == 'POST':
        company = Company.objects.get(pk=request.POST['company_match_id'])
        if request.POST['delegate_id'] != 'new':
            registrant = Registrants.objects.get(pk=request.POST['delegate_id'])
            registrant.company = company
            registrant.save()
    context = {
        'company': company,
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


def add_new_company(request):
    """ ajax call to add new company to database and link to current record """
    company = None
    company_match_list = None
    registrant = None
    company_select_form = CompanySelectForm()
    if request.method == 'POST':
        if request.POST['delegate_id'] != 'new':
            registrant = Registrants.objects.get(pk=request.POST['delegate_id'])
        company_select_form = CompanySelectForm(request.POST)
        if company_select_form.is_valid():
            company = company_select_form.save()
            if registrant:
                registrant.company = company
                registrant.save()
            company_select_form = CompanySelectForm()
        company_match_list = Company.objects.filter(
            name__icontains=request.POST['name']
        )
    context = {
        'company': company,
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
    # 1. instantiate various Nones
    current_registration = None
    new_delegate_form = NewDelegateForm()
    company_select_form = CompanySelectForm()
    new_company_form = NewCompanyForm()
    company_match_list = None
    assistant_form = AssistantForm()
    conference_select_form = ConferenceSelectForm()
    reg_details_form = RegDetailsForm()
    conference = None
    conference_options = None
    options_form = None
    registrant = None
    company = None
    assistant = None
    crm_match = None
    crm_match_list = None
    data_source = None

    # 2. verify that it's a POST and define objects based on POST data
    if request.method == 'POST':
        new_delegate_form = NewDelegateForm(request.POST)
        company_select_form = CompanySelectForm(request.POST)
        assistant_data = {
            'salutation': request.POST['assistant_salutation'],
            'first_name': request.POST['assistant_first_name'],
            'last_name': request.POST['assistant_last_name'],
            'title': request.POST['assistant_title'],
            'email': request.POST['assistant_email'],
            'phone': request.POST['assistant_phone'],
        }
        assistant_form = AssistantForm(assistant_data)
        conference_select_form = ConferenceSelectForm(request.POST)
        reg_details_form = RegDetailsForm(request.POST)
        if request.POST['current_regdetail_id']:
            current_registration = RegDetails.objects.get(
                pk=request.POST['current_regdetail_id']
            )
        if request.POST['event']:
            conference = Event.objects.get(pk=request.POST['event'])
        if request.POST['current_registrant_id']:
            registrant = Registrants.objects.get(
                pk=request.POST['current_registrant_id']
            )
        if request.POST['company_match_value']:
            company = Company.objects.get(pk=request.POST['company_match_value'])
        if request.POST['crm_match_value']:
            crm_match = Person.objects.get(pk=request.POST['crm_match_value'])
        if request.POST['assistant_match_value']:
            assistant = Assistant.objects.get(
                pk=request.POST['assistant_match_value']
            )
        if request.POST.getlist('event-option-selection'):
            option_list = []
            for option in request.POST.getlist('event-option-selection'):
                option_list.append(EventOptions.objects.get(pk=option))
        else:
            option_list = None
        valid_forms = "Valid Forms: "
        # 2a. verify that forms are valid and all data is present
        if new_delegate_form.is_valid():
            valid_forms += '<br/>new_delegate_form'
        else:
            valid_forms += '<br/>NOT new_delegate_form'
        if company_select_form.is_valid():
            valid_forms += '<br/>company_select_form'
        else:
            valid_forms += '<br/>NOT company_select_form'
        if assistant_form.is_valid():
            valid_forms += '<br/>assistant_form'
        else:
            valid_forms += '<br/>NOT assistant_form'
        if reg_details_form.is_valid():
            valid_forms += '<br/>reg_details_form'
        else:
            valid_forms += '<br/>NOT reg_details_form'
        # 2b. start processing
        return HttpResponse('<h1>Registration Processing Confirmation Page</h1>' \
                                '<h2>Stuff to go here<h2>' \
                                '<h3>%s<h3>' % valid_forms)

    context = {
        'current_registration': current_registration,
        'new_delegate_form': new_delegate_form,
        'company_select_form': company_select_form,
        'new_company_form': new_company_form,
        'company_match_list': company_match_list,
        'assistant_form': assistant_form,
        'conference_select_form': conference_select_form,
        'reg_details_form': reg_details_form,
        'conference': conference,
        'conference_options': conference_options,  # remove when form working
        'options_form': options_form,
        'registrant': registrant,
        'company': company,
        'assistant': assistant,
        'crm_match': crm_match,
        'crm_match_list': crm_match_list,
        'paid_status_values': PAID_STATUS_VALUES,
        'deposit_values': DEPOSIT_STATUS_VALUES,
        'cxl_values': CXL_VALUES,
        'sponsor_values': SPONSOR_VALUES,
        'data_source': data_source,
    }
    return render(request, 'delegate/index.html', context)
