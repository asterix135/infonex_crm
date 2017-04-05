import datetime
from io import BytesIO
import json
import os
import re

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.db.models import Q, Max, Count
from django.forms.models import model_to_dict
from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.datastructures import MultiValueDictKeyError

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from .forms import *
from .constants import *
from .pdfs import *
from crm.models import Person, Changes
from crm.views import add_change_record
from infonex_crm.settings import BASE_DIR
from registration.models import *
from registration.forms import ConferenceSelectForm


#############################
# HELPER FUNCTIONS
#############################
def build_email_message(reg_details, invoice):
    """
    Builds appropriate email message content with merge fields
    :param reg_details: RegDetails object
    :param invoice: Invoice object or None (if non-invoice registration)
    :returns email_message: str with email message - line breaks as \n
    """
    # Build merge paramaters
    email_merge_fields = {
        'event_name': reg_details.conference.title,
        'venue_name': '',
        'venue_details': '',
        'event_url': CANADA_WEBSITE,
        'reg_options': '',
        'cxl_policy': CANADA_CXL_POLICY,
        'account_rep_details': '',
        'registrar_details': 'Alona Glikin\n416-971-4177\naglikin@infonex.ca'
    }

    email_merge_fields['city'] = reg_details.conference.city
    if reg_details.conference.state_prov:
        email_merge_fields['city'] += ', ' + reg_details.conference.state_prov

    if reg_details.registrant.contact_option != 'A':
        email_merge_fields['whose_registration'] = 'your'
        email_merge_fields['who_is_registered'] = 'You are'
        if reg_details.registrant.salutation:
            email_merge_fields['salutation'] = reg_details.registrant.salutation + \
                ' ' + reg_details.registrant.last_name
        else:
            email_merge_fields['salutation'] = reg_details.registrant.first_name + \
                ' ' + reg_details.registrant.last_name
    else:
        email_merge_fields['whose_registration'] = \
            reg_details.registrant.first_name + ' ' + \
            reg_details.registrant.last_name + "'s"
        email_merge_fields['who_is_registered'] = \
            reg_details.registrant.salutation + ' ' + \
            reg_details.registrant.last_name + ' is'
        if reg_details.registrant.assistant.salutation:
            email_merge_fields['salutation'] = \
                reg_details.registrant.assistant.salutation + ' ' + \
                reg_details.registrant.assistant.last_name
        else:
            email_merge_fields['salutation'] = \
                reg_details.registrant.assistant.first_name + ' ' + \
                reg_details.registrant.assistant.last_name

    if reg_details.conference.hotel:
        email_merge_fields['venue_name'] = ' at the ' + \
            reg_details.conference.hotel.name
        email_merge_fields['venue_details'] = \
            '\nVenue Details are as follows:\n\n' + \
            reg_details.conference.hotel.name
        if reg_details.conference.hotel.address:
            email_merge_fields['venue_details'] += '\n' + \
                reg_details.conference.hotel.address
        venue_city = ''
        if reg_details.conference.hotel.city:
            venue_city += reg_details.conference.city
        if reg_details.conference.hotel.state_prov:
            if len(venue_city) > 0:
                venue_city += ', '
            venue_city += reg_details.conference.hotel.state_prov
        if reg_details.conference.hotel.postal_code:
            if len(venue_city) > 0:
                venue_city += ' '
            venue_city += reg_details.conference.hotel.postal_code
        if len(venue_city) > 0:
            email_merge_fields['venue_details'] += '\n' + venue_city
        if reg_details.conference.hotel.phone:
            email_merge_fields['venue_details'] += '\nVenue Phone: ' + \
                reg_details.conference.hotel.phone
        if reg_details.conference.hotel.hotel_url:
            email_merge_fields['venue_details'] += '\nVenue Web Site: ' + \
                reg_details.conference.hotel.hotel_url
        email_merge_fields['venue_details'] += '\n'

    if reg_details.conference.event_web_site:
        email_merge_fields['event_url'] = reg_details.conference.event_web_site
    elif reg_details.conference.company_brand == 'IT':
        email_merge_fields['event_url'] = TRAINING_CO_WEBSITE
    elif reg_details.conference.company_brand == 'IU':
        email_merge_fields['event_url'] = US_WEBSITE

    reg_option_list = []
    if reg_details.regeventoptions_set.all().count() > 0:
        for detail in reg_details.regeventoptions_set.all():
            start_date = detail.option.startdate.strftime('%-d %B, %Y')
            end_date = detail.option.enddate.strftime('%-d %B, %Y')
            conf_detail = detail.option.name + ' - ' + start_date
            if start_date != end_date:
                conf_detail += ' to ' + end_date
            reg_option_list.append(conf_detail)
    else:
        detail_date = reg_details.conference.date_begins.strftime('%-d %B, %Y')
        conf_detail = 'Conference - ' + detail_date
        reg_option_list.append(conf_detail)
    for option in reg_option_list:
        email_merge_fields['reg_options'] += option + '\n'

    if reg_details.conference.company_brand == 'IT':
        email_merge_fields['cxl_policy'] = TRAINING_CXL_POLICY
    elif reg_details.conference.company_brand == 'IU':
        email_merge_fields['cxl_policy'] = USA_CXL_POLICY

    if invoice:
        if invoice.sales_credit.groups.filter(name='sales').exists():
            rep = invoice.sales_credit
            if rep.first_name and rep.last_name:
                rep_details = 'Your account representative for this event ' \
                    'is: ' + rep.first_name + ' ' + rep.last_name + \
                    '.  If you have any questions, you can reach them at: ' + \
                    rep.email
                email_merge_fields['account_rep_details'] = rep_details

    registrar = reg_details.conference.registrar
    if registrar.first_name and registrar.last_name:
        registrar_details = registrar.first_name + ' ' + registrar.last_name
    else:
        registrar_details = 'Infonex Inc.'
    registrar_details += '\n416-971-4177\nEmail: ' + registrar.email
    email_merge_fields['registrar_details'] = registrar_details

    if reg_details.registration_status in GUEST_CONFIRMATION:
        email_body_path = os.path.join(
            BASE_DIR,
            'delegate/static/delegate/email_copy/guest_confirmation.txt'
        )
        if reg_details.registration_status == 'G':
            email_merge_fields['guest_status'] = 'as a Guest'
        elif reg_details.registration_status == 'SE':
            email_merge_fields['guest_status'] = 'with an Exhibit Pass'
        elif reg_details.registration_status == 'SD':
            email_merge_fields['guest_status'] = 'with a Sponsor Pass'
    elif reg_details.registration_status in SPONSOR_CONFIRMATION:
        email_body_path = os.path.join(
            BASE_DIR,
            'delegate/static/delegate/email_copy/sponsor_confirmation.txt'
        )
    else:
        email_body_path = os.path.join(
            BASE_DIR,
            'delegate/static/delegate/email_copy/delegate_confirmation.txt'
        )
    with open(email_body_path) as f:
        email_body = f.read()
    email_body = email_body.format(**email_merge_fields)

    return email_body


def build_email_subject(reg_details):
    if reg_details.registration_status in GUEST_CONFIRMATION:
        subject_line = 'Registration Confirmation '
    elif reg_details.registration_status in SPONSOR_CONFIRMATION:
        subject_line = 'Sponsorship Confirmation and Invoice '
    else:
        subject_line = 'Registration Confirmation and Invoice '
    subject_line += 'for Infonex Event: '
    subject_line += reg_details.conference.title
    return subject_line


def build_email_lists(reg_details, invoice):
    delegate_email = reg_details.registrant.email1
    if reg_details.registrant.assistant and \
        reg_details.registrant.assistant.email:
        assistant_email = reg_details.registrant.assistant.email
    else:
        assistant_email = None
    sales_rep_email = None
    if invoice and invoice.sales_credit:
        if (
            invoice.sales_credit.groups.filter(name='sales').exists() or
            invoice.sales_credit.groups.filter(name='sponsorship').exists()
        ):
            sales_rep_email = invoice.sales_credit.email
    registrar_email = reg_details.conference.registrar.email
    to_list = []
    cc_list = set()
    bcc_list = []
    if reg_details.registrant.contact_option == 'A' and assistant_email:
        to_list.append(assistant_email)
        cc_list.add(delegate_email)
    elif reg_details.registrant.contact_option == 'C':
        to_list.append(delegate_email)
        cc_list.add(assistant_email)
    else:
        to_list.append(delegate_email)
    if sales_rep_email:
        cc_list.add(sales_rep_email)
    bcc_list.append(registrar_email)
    return to_list, list(cc_list), bcc_list


def guess_company(company_name, postal_code, address1, city, name_first=False):
    """
    Helper function to guess company matches based on supplied info
    :param company_name:
    """
    if re.match(r'\b\w\d\w\d\w\d\b', postal_code):  # no space in postal code
        postal_code = postal_code.strip()[:3] + ' ' + postal_code.strip()[-3:]
    company_name_no_punct = re.sub('[!#?,.:";()]', '', company_name)
    company_name = company_name.strip()
    name_tokens = [x for x in company_name_no_punct.split()
                   if x.lower() not in STOPWORDS]
    company_best_guess = None
    company_suggest_list = []
    match0 = Company.objects.none()
    if name_first and postal_code in('', None) and city in ('', None):
        match1 = Company.objects.filter(name__iexact=company_name)
    elif name_first and city not in ('', None):
        match1 = Company.objects.filter(name__iexact=company_name,
                                        city__iexact=city)
    else:
        match1 = Company.objects.filter(name__iexact=company_name,
                                        postal_code__iexact=postal_code)
    if match1.count() == 1:
        company_best_guess = match1[0]
        company_suggest_list.extend(list(match1))
    elif match1.count() > 1:
        company_suggest_list.extend(list(match1))
        match0 = match1.filter(address1__iexact=address1)
        if match0.count() > 0:  # Choose the first one if more than one
            company_best_guess = match0[0]
        else:
            company_best_guess = match1[0]
    if name_first and postal_code in ('', None):
        name_tokens = [x for x in name_tokens if x.lower() not in STOPWORDS2]
        match_base = Company.objects.all()
    else:
        match_base = Company.objects.filter(postal_code=postal_code)

    # search for companies containing company name text as is
    match_contain = Company.objects.filter(name__icontains=company_name)
    if match_contain.count() > 0:
        if not company_best_guess:
            company_best_guess = match_contain[0]
        match_contain = match_contain.exclude(id__in=match1). \
            exclude(id__in=match0)
        company_suggest_list.extend(list(match_contain))

    # set up empty queries so things don't blowup
    match3 = Company.objects.none()
    match2 = Company.objects.none()

    # first, search on trigrams if feasible:
    if len(company_name.split()) > 3 and len(company_suggest_list) < 15:
        queries = []
        trigram_list = zip(company_name_no_punct.split(),
                           company_name_no_punct.split()[1:],
                           company_name_no_punct.split()[2:])
        for trigram in trigram_list:
            regex_term = r'[[:<:]]' + trigram[0].lower() + '[[:space:]]' + \
                trigram[1].lower() + '[[:space:]]' + trigram[2].lower()+ \
                '[[:>:]]'
            queries.append(Q(name__iregex=regex_term))
        query = queries.pop()
        for item in queries:
            query |= item
        match3 = match_base.filter(query)
        match3 = match3.exclude(id__in=match1).exclude(id__in=match0). \
            exclude(id__in=match_contain)
        if not company_best_guess and match3.count() > 0:
            company_best_guess = match3[0]
        company_suggest_list.extend(list(match3[:15-len(company_suggest_list)]))

    # search on bigrams if feasible/needed
    if len(company_name.split()) > 2 and len(company_suggest_list) < 15:
        queries = []
        bigram_list = zip(company_name_no_punct.split(),
                          company_name_no_punct.split()[1:])
        for bigram in bigram_list:
            regex_term = r'[[:<:]]' + bigram[0].lower() + '[[:space:]]' + \
                bigram[1].lower() + '[[:>:]]'
            queries.append(Q(name__iregex=regex_term))
        query = queries.pop()
        for item in queries:
            query |= item
        match2 = match_base.filter(query)
        match2 = match2.exclude(id__in=match0).exclude(id__in=match1). \
            exclude(id__in=match3).exclude(id__in=match_contain)
        if not company_best_guess and match2.count() > 0:
            company_best_guess = match2[0]
        company_suggest_list.extend(list(match2[:15-len(company_suggest_list)]))

    # search on tokens if still needed/feasible
    if 3 > len(name_tokens) > 0 and len(company_suggest_list) < 15:
        queries = []
        for token in name_tokens:
            regex_term = r'[[:<:]]' + token.lower() + '[[:>:]]'
            # queries.append(Q(name__icontain=token))
            queries.append(Q(name__iregex=regex_term))
        query=queries.pop()
        for item in queries:
            query |= item
        match_token = match_base.filter(query)
        match_token = match_token.exclude(id__in=match0). \
            exclude(id__in=match1).exclude(id__in=match2). \
            exclude(id__in=match3).exclude(id__in=match_contain)
        if not company_best_guess and match_token.count() > 0:
            company_best_guess = match_token[0]
        company_suggest_list.extend(list(match_token[:15-len(company_suggest_list)]))
    return company_best_guess, company_suggest_list


def process_complete_registration(request, assistant_data, company, crm_match,
                                  current_registration, reg_details_data,
                                  registrant, conference, option_list):
    """
    Helper function, called from process_registration once request data
    has been verified
    """
    # 1. create database records if not present
    # a. assistant
    if request.POST['assistant_match_value']:
        assistant = Assistant.objects.get(
            pk=request.POST['assistant_match_value']
        )
        assistant_form = AssistantForm(assistant_data, instance=assistant)
        print(assistant)
        assistant_form.save()
    elif assistant_data:
        # Check to make sure record not already in the database
        assistant_db_check = Assistant.objects.filter(
            first_name=assistant_data['first_name'],
            last_name=assistant_data['last_name'],
            email=assistant_data['email'],
        )
        if assistant_db_check.count() > 0:
            assistant=assistant_db_check[0]
            assistant_form = AssistantForm(assistant_data, instance=assistant)
            assistant_form.save()
        else:
            assistant = AssistantForm(assistant_data).save()
    else:
        assistant = None

    # b. Update company with form values
    company_select_form = CompanySelectForm(request.POST, instance=company)
    company_select_form.save()
    if company.country and company.country.lower() not in ('', 'canada'):
        if re.match(r'\b\w\d\w\d\w\d\b', company.postal_code):  # no space
            new_pc = company.postal_code.strip()
            copmany.postal_code = new_pc[:3] + ' ' + new_pc[-3:]
            company.save()

    # c. update crm record with form values
    crm_match.name = request.POST['first_name'] + ' ' + request.POST['last_name']
    crm_match.title = request.POST['title']
    crm_match.company = request.POST['crm_company']
    crm_match.phone = request.POST['phone1']
    crm_match.email = request.POST['email1']
    crm_match.city = request.POST['city']
    crm_match.date_modified = timezone.now()
    crm_match.modified_by = request.user
    crm_match.save()
    add_change_record(crm_match, 'update')

    # d. registrant
    if registrant:
        delegate_form = NewDelegateForm(request.POST, instance=registrant)
        delegate_form.save()
        registrant.assistant = assistant
        registrant.modified_by = request.user
        registrant.date_modified = timezone.now()
        registrant.save()
    else:
        registrant_db_check = Registrants.objects.filter(
            company=company,
            first_name=request.POST['first_name'],
            last_name=request.POST['last_name'],
            email1=request.POST['email1']
        )
        if registrant_db_check.count() > 0:
            registrant = registrant_db_check[0]
            delegate_form = NewDelegateForm(request.POST, instance=registrant)
            delegate_form.save()
            registrant.assistant = assistant
            registrant.modified_by = request.user
            registrant.date_modified = timezone.now()
            registrant.save()
        else:
            registrant = Registrants(
                crm_person=crm_match,
                assistant=assistant,
                company=company,
                salutation=request.POST['salutation'],
                first_name=request.POST['first_name'],
                last_name=request.POST['last_name'],
                title=request.POST['title'],
                email1=request.POST['email1'],
                email2=request.POST['email2'],
                phone1=request.POST['phone1'],
                phone2=request.POST['phone2'],
                contact_option=request.POST['contact_option'],
                # delegate_notes=request.POST['delegate_notes'],
                created_by=request.user,
                date_created=timezone.now(),
                modified_by=request.user,
                date_modified=timezone.now(),
            )
            registrant.save()

    # e. reg_details
    if not current_registration:
        reg_detail_db_check = RegDetails.objects.filter(
            conference=conference,
            registrant=registrant
        )
        if reg_detail_db_check.count() > 0 and \
            reg_detail_db_check[0].registration_status not in ('SP', 'SU'):
            current_registration = reg_detail_db_check[0]
        else:
            current_registration = RegDetails(
                date_created=timezone.now(),
                created_by=request.user,
            )
        current_registration.conference = conference
        current_registration.registrant = registrant
    elif conference != current_registration.conference:
        raise ValueError('\nConference changed for registration\n')
    current_registration.register_date = request.POST['register_date']
    if request.POST['cancellation_date'] != '':
        current_registration.cancellation_date = \
            request.POST['cancellation_date']
    else:
        current_registration.cancellation_date = None
    current_registration.registration_status = \
        request.POST['registration_status']
    current_registration.registration_notes = request.POST['registration_notes']
    current_registration.modified_by = request.user
    current_registration.date_modified = timezone.now()
    current_registration.save()

    # f. invoice details
    try:
        current_invoice = Invoice.objects.get(reg_details=current_registration)
    except Invoice.DoesNotExist:
        # The following ensures that we can issue more than one Invoice
        # to a sponsor (for partial payments)
        if current_registration.registration_status in NON_INVOICE_VALUES:
            current_invoice = None
        else:
            current_invoice = Invoice(
                reg_details=current_registration,
            )
    if current_invoice:
        reg_details_form = RegDetailsForm(reg_details_data,
                                          instance=current_invoice)
        reg_details_form.save()

    # g. Event Options (if applicable)
    if len(option_list) > 0:
        for option in option_list:
            new_option = RegEventOptions(
                reg=current_registration,
                option=option
            )
            new_option.save()

    return current_registration, registrant, assistant


#############################
# VIEW FUNCTIONS
#############################
@login_required
def confirmation_details(request):
    """
    Renders confirmation_details page
    as redirect from form submission on index
    """
    reg_details = RegDetails.objects.get(
        pk=request.session['current_registration']
    )
    try:
        invoice = Invoice.objects.get(reg_details=reg_details)
    except Invoice.DoesNotExist:
        invoice = None
    email_body = build_email_message(reg_details, invoice)
    email_subject = build_email_subject(reg_details)
    to_list, cc_list, bcc_list = build_email_lists(reg_details, invoice)

    registrant = Registrants.objects.get(pk=request.session['registrant'])
    if request.session['assistant']:
        assistant = Assistant.objects.get(pk=request.session['assistant'])
    else:
        assistant = None

    context = {
        'current_registration': reg_details,
        'registrant': registrant,
        'assistant': assistant,
        'email_body': email_body,
        'email_subject': email_subject,
        'to_list': to_list,
        'cc_list': cc_list,
        'bcc_list': bcc_list,
        'invoice': invoice,
    }
    return render(request, 'delegate/confirmation_details.html', context)


@login_required
def index(request):
    """ renders base delegate/index.html page """
    if request.method == 'GET' and 'reg_id' in request.GET:
        try:
            current_registration = RegDetails.objects.get(
                pk=request.GET['reg_id']
            )
        except RegDetails.DoesNotExist:
            raise Http404('That Registration does not exist')
    elif request.method != 'POST':
        return redirect('/registration/')

    # Instantiate stuff
    new_delegate_form = NewDelegateForm()
    company_select_form = CompanySelectForm()
    new_company_form = NewCompanyForm()
    company_match_list = None
    assistant_form = AssistantForm()
    conference_select_form = ConferenceSelectForm()
    reg_details_form = RegDetailsForm()
    if 'current_registration' not in locals():
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

    # Deal with passed data
    if request.method == 'POST':
        conf_id = request.POST['conf_id']
        conference = Event.objects.get(pk=conf_id)
        crm_id = request.POST['crm_id']
        registrant_id = request.POST['registrant_id']
    else:
        conference = current_registration.conference
        conf_id = conference.pk
        try:
            crm_id = current_registration.registrant.crm_person.pk
        except AttributeError:
            crm_id = None
        registrant_id = current_registration.registrant.pk
    conference_options = conference.eventoptions_set.all()
    options_form = OptionsForm(conference)
    conference_select_form = ConferenceSelectForm({'event': conf_id})
    if registrant_id != '':
        registrant = Registrants.objects.get(pk=registrant_id)
        new_delegate_form = NewDelegateForm(instance=registrant)
        company = registrant.company
        company_select_form = CompanySelectForm(instance=company)
        assistant = registrant.assistant
        if assistant:
            assistant_form = AssistantForm(instance=assistant)
        if registrant.crm_person:
            crm_match = Person.objects.get(pk=registrant.crm_person.id)
        try:
            if not current_registration:
                current_registration = RegDetails.objects.get(
                    registrant=registrant, conference=conference
                )
                data_source = 'delegate'
            reg_data = {
                'register_date': current_registration.register_date,
                'cancellation_date': current_registration.cancellation_date,
                'registration_status': current_registration.registration_status,
                'registration_notes': current_registration.registration_notes,
            }
            if hasattr(current_registration, 'invoice'):
                invoice = current_registration.invoice
                reg_data['sales_credit'] = invoice.sales_credit
                reg_data['pre_tax_price'] = invoice.pre_tax_price
                reg_data['gst_rate'] = invoice.gst_rate
                reg_data['hst_rate'] = invoice.hst_rate
                reg_data['qst_rate'] = invoice.qst_rate
                reg_data['payment_date'] = invoice.payment_date
                reg_data['payment_method'] = invoice.payment_method
                reg_data['fx_conversion_rate'] = invoice.fx_conversion_rate
                reg_data['invoice_notes'] = invoice.invoice_notes
                reg_data['sponsorship_description'] = \
                    invoice.sponsorship_description
            else:
                if registrant.company.gst_hst_exempt:
                    reg_data['gst_rate'] = 0
                    reg_data['hst_rate'] = 0
                if registrant.company.qst_exempt:
                    reg_data['qst_rate'] = 0
            reg_details_form = RegDetailsForm(initial=reg_data)
        except RegDetails.DoesNotExist:
            reg_data = {}
            if registrant.company.gst_hst_exempt:
                reg_data['gst_rate'] = 0
                reg_data['hst_rate'] = 0
            if registrant.company.qst_exempt:
                reg_data['qst_rate'] = 0
            if len(reg_data) > 0:
                reg_details_form = RegDetailsForm(initial = reg_data)
        data_source = 'delegate'
    elif crm_id != '':  # No registrant, so try CRM
        crm_match = Person.objects.get(pk=crm_id)
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
        new_delegate_form = NewDelegateForm(initial=form_data)
        company_select_form = CompanySelectForm(
            initial={'name': crm_match.company,
                     'name_for_badges': crm_match.company[:30],
                      'city': crm_match.city,
                     }
        )
        data_source = 'crm'
    else:  # neither reg_id or crm_id means new Person
        data_source = 'new'
    context = {
        'current_registration': current_registration,
        'new_delegate_form': new_delegate_form,
        'company_select_form': company_select_form,
        'new_company_form': new_company_form,
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
        'paid_status_values': PAID_STATUS_VALUES,
        'cxl_values': CXL_VALUES,
        'non_invoice_values': NON_INVOICE_VALUES,
        'data_source': data_source,
        'total_tax_amount': None,
        'total_invoice_amount': None,
    }
    return render(request, 'delegate/index.html', context)


@login_required
def process_registration(request):
    """ form submission """
    # 1. instantiate various Nones
    current_registration = None
    new_delegate_form = NewDelegateForm()
    company_select_form = CompanySelectForm()
    new_company_form = NewCompanyForm()
    company_match_list = None
    assistant_data = None
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
    company_error = None
    assistant_missing = None
    option_selection_needed = None
    option_list = []
    # 2. verify that it's a POST and define objects based on POST data
    if request.method == 'POST':
        # Populate forms with appropriate data
        new_delegate_form = NewDelegateForm(request.POST)
        company_select_form = CompanySelectForm(request.POST)
        if (request.POST['assistant_first_name'] != '' or
            request.POST['assistant_last_name'] != '' or
            request.POST['assistant_title'] != '' or
            request.POST['assistant_email'] != '' or
            request.POST['assistant_phone'] != ''):
            assistant_data = {
                'salutation': request.POST['assistant_salutation'],
                'first_name': request.POST['assistant_first_name'],
                'last_name': request.POST['assistant_last_name'],
                'title': request.POST['assistant_title'],
                'email': request.POST['assistant_email'],
                'phone': request.POST['assistant_phone'],
            }
            assistant_form = AssistantForm(assistant_data)
        current_time = timezone.now()
        reg_details_data = {
            'sales_credit': request.POST['sales_credit'],
            'pre_tax_price': request.POST['pre_tax_price'],
            'gst_rate': request.POST['gst_rate'] if 'gst_rate' in \
                request.POST else 0,
            'hst_rate': request.POST['hst_rate'] if 'hst_rate' in \
                request.POST else 0,
            'qst_rate': request.POST['qst_rate'] if 'qst_rate' in \
                request.POST else 0,
            'payment_date': request.POST['payment_date'] if 'payment_date' in \
                request.POST else None,
            'payment_method': request.POST['payment_method'] if \
                'payment_method' in request.POST else None,
            'fx_conversion_rate': request.POST['fx_conversion_rate'] if \
                'fx_conversion_rate' in request.POST else 1,
            'register_date': request.POST['register_date'] if (
                'register_date' in request.POST and
                request.POST['register_date'] != ''
            ) else None,
            'cancellation_date': request.POST['cancellation_date'] if \
                'cancellation_date' in request.POST else None,
            'registration_status': request.POST['registration_status'],
            'invoice_notes': request.POST['invoice_notes'],
            'registration_notes': request.POST['registration_notes'],
            'sponsorship_description': request.POST['sponsorship_description'] \
                if 'sponsorship_description' in request.POST else None
        }
        if request.POST['registration_status'] in NON_INVOICE_VALUES:
            reg_details_data['sales_credit'] = request.user.pk
        reg_details_form = RegDetailsForm(reg_details_data)
        if request.POST['current_regdetail_id']:
            current_registration = RegDetails.objects.get(
                pk=request.POST['current_regdetail_id']
            )

        # set up various objects if present in form
        if request.POST['current_registrant_id']:
            registrant = Registrants.objects.get(
                pk=request.POST['current_registrant_id']
            )

        if request.POST['company_match_value'] not in ('new', ''):
            company = Company.objects.get(pk=request.POST['company_match_value'])
        elif request.POST['company_match_value'] == 'new':
            if company_select_form.is_valid():
                company = company_select_form.save()
            else:
                company_error = True
        else:
            company_error = True

        if request.POST['crm_match_value'] not in ('', 'new') and \
            not company_error:
            crm_match = Person.objects.get(pk=request.POST['crm_match_value'])
        else:
            crm_match = Person(
                name=request.POST['first_name'] + ' ' + \
                     request.POST['last_name'],
                title=request.POST['title'],
                company=request.POST['crm_company'],
                phone=request.POST['phone1'],
                email=request.POST['email1'],
                city=company.city,
                date_created=timezone.now(),
                created_by=request.user,
                date_modified=timezone.now(),
                modified_by=request.user,
            )
            crm_match.save()
            add_change_record(crm_match, 'reg_add')
        if request.POST['selected_conference_id']:
            conference = Event.objects.get(
                pk=request.POST['selected_conference_id']
            )
        if request.POST['assistant_match_value']:
            assistant = Assistant.objects.get(
                pk=request.POST['assistant_match_value']
            )

        # ensure that various values are correctly submitted

        if request.POST['contact_option'] in ['A', 'C'] and not \
            request.POST['assistant_email']:
            assistant_missing = True
        if request.POST.getlist('event-option-selection'):
            for option in request.POST.getlist('event-option-selection'):
                option_list.append(EventOptions.objects.get(pk=option))
        if len(option_list) == 0 and len(conference.eventoptions_set.all()) > 1:
            option_selection_needed = True
        elif len(option_list) == 0 and len(
            conference.eventoptions_set.all()) == 1:
            option_list.append(conference.eventoptions_set.all()[0])

        # ensure everything is valid, then process registration
        if new_delegate_form.is_valid() and company_select_form.is_valid() \
            and (not assistant_data or assistant_form.is_valid()) \
            and reg_details_form.is_valid() \
            and not company_error and not assistant_missing \
            and not option_selection_needed and conference:

            current_registration, registrant, assistant = \
                process_complete_registration(request, assistant_data, company,
                                              crm_match, current_registration,
                                              reg_details_data, registrant,
                                              conference, option_list)
            request.session['current_registration'] = current_registration.pk
            request.session['registrant'] = registrant.pk
            request.session['assistant'] = assistant.pk if assistant else None
            return redirect('/delegate/confirmation_details')

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
        'cxl_values': CXL_VALUES,
        'non_invoice_values': NON_INVOICE_VALUES,
        'data_source': data_source,
        'company_error': company_error,
        'assistant_missing': assistant_missing,
        'option_selection_needed': option_selection_needed,
    }
    return render(request, 'delegate/index.html', context)


#######################
# AJAX Calls
#######################
@login_required
def conf_has_regs(request):
    if request.method != 'POST':
        return HttpResponse('')
    conference = get_object_or_404(Event, pk=request.POST['conf_id'])
    if RegDetails.objects.filter(conference=conference).count() > 0:
        first_reg = 'true'
    else:
        first_reg = 'false'
    context = {
        'first_reg': first_reg,
        'conference': conference,
    }
    return render(request, 'delegate/addins/conf_setup_modal.html', context)


@login_required
def company_crm_modal(request):
    """
    generates suggested matches for company record and crm record on any
    new registration and feeds those to a modal pop-up on the
    delegate/index.html page
    """
    if request.method != 'POST':
        return HttpResponse('')
    # Set up various variables
    company = None
    crm_match = None
    company_suggest_list = None
    crm_suggest_list = None
    company_best_guess = None  # This is a company object or None
    crm_best_guess = None  # This is a person object or None
    if request.POST['company_id'] != '':
        try:
            company = Company.objects.get(pk=request.POST['company_id'])
        except Company.DoesNotExist:
            pass
    if request.POST['crm_id'] != '':
        try:
            crm_match = Person.objects.get(pk=request.POST['crm_id'])
        except Person.DoesNotExist:
            pass
    company_name = request.POST['company_name']
    address1 = request.POST['address1']
    address2 = request.POST['address2']
    city = request.POST['city']
    state_prov = request.POST['state_prov']
    postal_code = request.POST['postal_code']
    first_name = request.POST['first_name']
    last_name = request.POST['last_name']
    title = request.POST['title']
    email = request.POST['email']

    # generate company suggestions
    if not company:
        company_best_guess, company_suggest_list = guess_company(
            company_name, postal_code, address1, city
        )

    if not crm_match:
        name_tokens = company_name.split()
        person_name = first_name + ' ' + last_name
        match0 = Person.objects.none()
        if email != '':
            match1 = Person.objects.filter(email=email)
        else:
            match1 = Person.objects.none()
        if match1.count() == 1:
            crm_best_guess = match1[0]
        elif match1.count() > 1:
            match0 = match1.filter(name=person_name)
            if match0.count() > 1:
                crm_best_guess = match0[0]
                match0 = match0.filter(company=company_name)
                if match0.count() > 0:
                    crm_best_guess = match0[0]
            elif match0.count() == 1:
                crm_best_guess = match0[0]
            else:
                crm_best_guess = match1[1]
        crm_suggest_list = match0 | match1
        if crm_suggest_list.count() < 10:
            match2 = Person.objects.filter(name=person_name,
                                           company=company_name)
            if not crm_best_guess and match2.count() > 0:
                crm_best_guess = match2[0]
            crm_suggest_list = crm_suggest_list | match2
        if crm_suggest_list.count() < 10:
            name_qs1 = Person.objects.filter(name__icontains=first_name,
                                             company=company_name)
            name_qs2 = Person.objects.filter(name__icontains=last_name,
                                             company=company_name)
            crm_suggest_list = crm_suggest_list | name_qs1 | name_qs2
            if not crm_best_guess and crm_suggest_list.count() > 0:
                crm_best_guess = crm_suggest_list[0]
        if crm_suggest_list.count() < 10 and len(name_tokens) > 0:
            match3 = Person.objects.filter(name=person_name)
            queries = []
            for token in name_tokens:
                queries.append(Q(company__icontains=token))
            query = queries.pop()
            for item in queries:
                query |= item
            match3 = match3.filter(query)
            if not crm_best_guess and match3.count() > 0:
                crm_best_guess = match3[0]
            crm_suggest_list = crm_suggest_list | match3[:10]
        if crm_suggest_list.count() < 10 and len(name_tokens) > 0:
            match4_a = Person.objects.filter(name__icontains=first_name)
            match4_b = Person.objects.filter(name__icontains=last_name)
            match4 = match4_a | match4_b
            match4 = match4.filter(company__icontains=company_name)
            if match4.count() > 10:
                crm_suggest_list = list(set(list(crm_suggest_list) +
                                            list(match4[:10])))
            else:
                crm_suggest_list = crm_suggest_list | match4

    context = {
        'company': company,
        'crm_match': crm_match,
        'company_suggest_list': company_suggest_list,
        'crm_suggest_list': crm_suggest_list,
        'company_best_guess': company_best_guess,
        'crm_best_guess': crm_best_guess,
    }
    return render(request, 'delegate/addins/company_crm_modal.html', context)


@login_required
def get_company_details(request):
    if 'company' not in request.GET:
        company = None
    else:
        try:
            company = Company.objects.get(pk=request.GET['company'])
        except (Company.DoesNotExist, MultiValueDictKeyError, ValueError):
            company = None
    if company:
        company_data = model_to_dict(company)
    else:
        company_data = {'id': None}
    return JsonResponse(company_data)


@login_required
def person_is_registered(request):
    """
    Checks whether the current delegate is registered for a conference
    """
    if request.method != 'POST':
        return HttpResponse('')
    if request.POST['registrant_id'] != '':
        registrant = get_object_or_404(Registrants,
                                       pk=request.POST['registrant_id'])
        new_conference = get_object_or_404(Event, pk=request.POST['conf_id'])
        try:
            reg_detail = RegDetails.objects.get(conference=new_conference,
                                                registrant=registrant)
        except RegDetails.DoesNotExist:
            reg_detail = None
    else: reg_detail = None
    return HttpResponse('<div><input type="hidden" ' \
                        'id="person-is-registered" ' \
                        'name="person-is-registered" value="' + \
                        str(reg_detail is not None) + '" />')


@login_required
def search_for_substitute(request):
    if set(('conf_id', 'first_name', 'last_name', 'company_id')) > \
        request.GET.keys():
        return HttpResponse('')
    try:
        conference = Event.objects.get(pk=request.GET['conf_id'])
    except Event.DoesNotExist:
        raise Http404('Conference does not exist')
    try:
        company = Company.objects.get(pk=request.GET['company_id'])
    except Company.DoesNotExist:
        raise Http404('Company does not exist')
    context = {
        'foo': 0
    }
    return render(request, 'delegate/addins/substitute_match_list.html',
                  context)


@login_required
def suggest_company(request):
    """
    Ajax call (I think?) - returns json of top 25 companies (by number in db)
    that match entered string
    """
    query_term = request.GET.get('q', '')
    selects = Company.objects.filter(name__icontains=query_term) \
        .values('name').annotate(total=Count('name')) \
        .order_by('-total')[:25]
    results = []
    for select in selects:
        select_json = {}
        select_json['identifier'] = select['name']
        results.append(select_json)
    data = json.dumps(results)
    mimetype = 'applications/json'
    return HttpResponse(data, mimetype)


@login_required
def suggest_company_match(request):
    if request.method != 'POST':
        return HttpResponse('')
    company_name = request.POST['company_name']
    postal_code = request.POST['postal_code']
    city = request.POST['city']
    address1 = request.POST['address1']
    company_best_guess, company_suggest_list = guess_company(
        company_name, postal_code, address1, city, name_first=True
    )
    context = {
        'company_suggest_list': company_suggest_list,
        'company_best_guess': company_best_guess,
    }
    return render(request, 'delegate/addins/company_suggestion_matches.html',
                  context)


@login_required
def update_conference_options(request):
    """ ajax call to update conference options when event is changed """
    conference_options = None
    if request.method == 'POST':
        conf_id = request.POST['conf_id']
        conference = Event.objects.get(pk=conf_id)
        conference_options = conference.eventoptions_set.all()
    context = {'conference_options': conference_options}
    return render(request, 'delegate/addins/conference_options.html', context)


@login_required
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


@login_required
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


@login_required
def update_payment_details(request):
    """ ajax call to update payment details """
    reg_details_form = RegDetailsForm()
    if request.method == 'POST':
        form_data = {'registration_status': request.POST['reg_status'],
                     'payment_method': None}
        if request.POST['reg_status'] in PAID_STATUS_VALUES:
            form_data['payment_date'] = timezone.now()
        if request.POST['regdetail_id'] != 'new':
            current_reg = RegDetails.objects.get(
                pk=request.POST['regdetail_id']
            )
            if current_reg.invoice:
                form_data['sponsorship_description'] = \
                    current_reg.invoice.sponsorship_description
                form_data['payment_date'] = current_reg.invoice.payment_date
                form_data['payment_method'] = \
                    current_reg.invoice.payment_method
                reg_details_form = RegDetailsForm(
                    form_data, instance=current_reg.invoice
                )
        else:
            reg_details_form = RegDetailsForm(form_data)
    context = {
        'reg_details_form': reg_details_form,
        'paid_status_values': PAID_STATUS_VALUES,
    }
    return render(request, 'delegate/addins/status_based_reg_fields.html',
                  context)


@login_required
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
        if request.POST['company_id'] not in ('', 'new'):
            reg_form_data = {}
            company = get_object_or_404(Company, request.POST['conf_id'])
            if company.gst_hst_exempt:
                reg_form_data['gst_rate'] = 0
                reg_form_data['hst_rate'] = 0
            if company.qst_exempt:
                reg_form_data['qst_rate'] = 0
            reg_details_form = RegDetailsForm(reg_form_data)
    context = {'conference': conference,
               'reg_details_form': reg_details_form}
    return render(request, 'delegate/addins/delegate_tax_information.html',
                  context)


############################
# GRAPHICS/DOCUMENTS
############################
@login_required
def get_invoice(request):
    reg_details = get_object_or_404(RegDetails, pk=request.GET.get('reg', ''))
    invoice = get_object_or_404(Invoice, reg_details=reg_details)
    file_details = 'inline; filename="invoice_' + str(invoice.pk) + '"'
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = file_details
    buffr = BytesIO()
    invoice_pdf = canvas.Canvas(buffr, pagesize=letter)
    generate_invoice(invoice_pdf, reg_details, invoice)
    invoice_pdf.showPage()
    invoice_pdf.save()
    pdf = buffr.getvalue()
    buffr.close()
    response.write(pdf)
    return response


@login_required
def get_reg_note(request):
    reg_details = get_object_or_404(RegDetails, pk=request.GET.get('reg', ''))
    try:
        invoice = Invoice.objects.get(reg_details=reg_details)
    except Invoice.DoesNotExist:
        invoice = None
    inv_num = str(invoice.pk) if invoice else 'free'
    file_details = 'inline; filename="reg_note_' + inv_num + '"'
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = file_details
    buffr = BytesIO()
    note_pdf = canvas.Canvas(buffr, pagesize=letter)
    generate_reg_note(note_pdf, reg_details, invoice)
    note_pdf.showPage()
    note_pdf.save()
    pdf = buffr.getvalue()
    buffr.close()
    response.write(pdf)
    return response


@login_required
def send_conf_email(request):
    if request.method != 'POST':
        return HttpResponse('')
    reg_details = get_object_or_404(RegDetails,
                                    pk=request.POST['reg_id'])
    try:
        invoice = Invoice.objects.get(reg_details=reg_details)
    except Invoice.DoesNotExist:
        invoice = None
    if invoice:
        buffr = BytesIO()
        invoice_pdf = canvas.Canvas(buffr, pagesize=letter)
        generate_invoice(invoice_pdf, reg_details, invoice)
        invoice_pdf.showPage()
        invoice_pdf.save()
        pdf = buffr.getvalue()
        buffr.close()

    email_body = request.POST['email_message']
    email_body = email_body.replace('\n', '<br/>')
    email_subject = request.POST['email_subject']
    to_list = list(set(request.POST.getlist('to_list[]')))
    cc_list = list(set(request.POST.getlist('cc_list[]')))
    bcc_list = list(set(request.POST.getlist('bcc_list[]')))
    email = EmailMessage(
        subject=email_subject,
        body=email_body,
        to=to_list,
        cc=cc_list,
        bcc=bcc_list,
    )
    if pdf:
        filename = 'invoice-' + str(invoice.pk) + '.pdf'
        email.attach(filename, pdf, 'application/pdf')
    email.content_subtype = 'html'
    # email.send()
    return HttpResponse(status=204)
