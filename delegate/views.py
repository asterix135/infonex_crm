import datetime
from io import BytesIO
import json
import os
import re

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.db.models import Q, Max, Count
from django.forms.forms import DeclarativeFieldsMetaclass  # For isinstance
from django.forms.models import model_to_dict, ModelFormMetaclass
from django.http import HttpResponse, JsonResponse, Http404, \
        HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.datastructures import MultiValueDictKeyError
from django.views.generic import FormView, ListView, TemplateView
from django.views.generic.edit import ModelFormMixin

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from .guess_company import guess_company, iteratively_replace_and_guess_name
from crm.mixins import ChangeRecord
from crm.models import Person, Changes
from crm.views import add_change_record
from delegate.constants import *
from delegate.forms import *
from delegate.mixins import ProcessCompleteRegistration, GuessCompanyMixin
from delegate.models import QueuedOrder
from delegate.pdfs import *
from infonex_crm.settings import BASE_DIR
from registration.mixins import RegistrationPermissionMixin
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
        'room_rate': '',
        'event_url': CANADA_WEBSITE,
        'reg_options': '',
        'cxl_policy': CANADA_CXL_POLICY,
        'account_rep_details': '',
        'registrar_details': 'Registration Department\n416-971-4177\nregister@infonex.ca'
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
            email_merge_fields['salutation'] = \
                (reg_details.registrant.first_name or '') + \
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

        # If have hotel, then build room block info if available:
        if reg_details.conference.room_rate:
            email_merge_fields['room_rate'] = \
                'Please note the following details to book a room: \n\n'
            email_merge_fields['room_rate'] += reg_details.conference.room_rate
            email_merge_fields['room_rate'] += '\n\n'

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
    elif reg_details.conference.date_begins - datetime.timedelta(weeks=4) <= \
        datetime.date.today():
        email_merge_fields['cxl_policy'] = TWO_WEEK_CXL_POLICY
    elif reg_details.conference.company_brand == 'IU':
        email_merge_fields['cxl_policy'] = USA_CXL_POLICY

    if invoice:
        if invoice.sales_credit.groups.filter(name='sales').exists():
            rep = invoice.sales_credit
            if rep.first_name and rep.last_name:
                contact_info_added = False
                rep_details = 'Your account representative for this event ' \
                    'is: ' + rep.first_name + ' ' + rep.last_name + '.'
                if rep.email:
                    rep_details += ' If you have any questions, you can ' \
                        'reach them at: ' + rep.email
                    contact_info_added = True
                if rep.userprofile.phone:
                    if contact_info_added:
                        rep_details += ' or by phone at: ' + rep.userprofile.phone
                    else:
                        rep_details += ' If you have any questions, you can ' \
                            'reach them at: ' + rep.userprofile.phone
                email_merge_fields['account_rep_details'] = rep_details

    registrar = reg_details.conference.registrar
    registrar_string = ''
    if registrar.first_name and registrar.last_name:
        registrar_string += registrar.first_name + ' ' + \
            registrar.last_name + '\n'
    else:
        registrar_string += 'Infonex Registration Department\n'
    if registrar.userprofile.phone:
        registrar_string += registrar.userprofile.phone + '\n'
    else:
        registrar_string += '416-971-4177\n'
    if registrar.email:
        registrar_string += registrar.email
    else:
        registrar_string += 'register@infonex.ca'
    email_merge_fields['registrar_details'] = registrar_string

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
    elif datetime.date.today() >= reg_details.conference.date_begins:
        email_body_path = os.path.join(
            BASE_DIR,
            'delegate/static/delegate/email_copy/post_event_confirmation.txt'
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


def guess_by_ngrams(company_name):
    """
    generates list of companies that match current company by n-grams
    """
    company_name = ' '.join(company_name.lower().strip().split())
    match_set = Company.objects.none()
    if len(company_name.split()) > 3:
        queries = []
        trigram_list = zip(company_name.split(),
                           company_name.split()[1:],
                           company_name.split()[2:])
        for trigram in trigram_list:
            if trigram[0] not in STOPWORDS \
                or trigram[1] not in STOPWORDS \
                or trigram[2] not in STOPWORDS:
                    search_term = ' '.join(trigram)
                    queries.append(Q(name__icontains=search_term))
        if len(queries) > 0:
            query = queries.pop()
            for item in queries:
                query |= item
            match_set = Company.objects.filter(query)
    if len(company_name.split()) > 2 and match_set.count() < 15:
        queries = []
        bigram_list = zip(company_name.split(),
                          company_name.split()[1:])
        for bigram in bigram_list:
            if bigram[0] not in STOPWORDS \
                or bigram[1] not in STOPWORDS:
                search_term = ' '.join(bigram)
                queries.append(Q(name__icontains=search_term))
        if len(queries) > 0:
            query = queries.pop()
            for item in queries:
                query |= item
            bigram_set = Company.objects.filter(query)
            match_set = match_set | bigram_set
    if match_set.count() < 15:
        queries = []
        name_tokens = [x for x in company_name.split() if x not in STOPWORDS]
        for token in name_tokens:
            queries.append(Q(name__icontains=token))
        if len(queries) > 0:
            query = queries.pop()
            for item in queries:
                query |= item
            keyword_set = Company.objects.filter(query)
            match_set = match_set | keyword_set
    return match_set


#############################
# VIEW FUNCTIONS
#############################
@login_required
def confirmation_details(request):
    """
    Renders confirmation_details page
    as redirect from form submission on index
    """
    try:
        reg_details = RegDetails.objects.get(
            pk=request.session['current_registration']
        )
    except KeyError:
        return redirect('/registration/')
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
        'reg_action': request.session['reg_action'],
    }
    return render(request, 'delegate/confirmation_details.html', context)


class Index(RegistrationPermissionMixin, TemplateView):
    template_name = 'delegate/index.html'
    redirect_url = '/registration/'
    all_forms = {
        'new_delegate_form': NewDelegateForm,
        'company_select_form': CompanySelectForm,  # 3/4 set in _with_registrant, _with_crm_value, _with_new,
        'new_company_form': NewCompanyForm,
        'assistant_form': AssistantForm,
        'conference_select_form': ConferenceSelectForm, # set in _set_conference_details
        'reg_details_form': RegDetailsForm,
        'options_form': OptionsForm,  # set in _set_conference_details
    }
    queued_order_id = None
    additional_context = {}

    def _check_for_existing_regdetails(self):
        try:
            self.current_registration = RegDetails.objects.get(
                registrant=self.registrant, conference=self.conference
            )
            self.action_type = 'edit'
        except RegDetails.DoesNotExist:
            self.current_registration = None

    def _instantiate_model_form(self, form_klass_name,
                                instance=None, initial=None):
        if instance is not None:
            self.all_forms[form_klass_name] = self.all_forms[form_klass_name](
                instance=instance
            )
        elif initial is not None:
            self.all_forms[form_klass_name] = self.all_forms[form_klass_name](
                initial=initial
            )
        else:
            self.all_forms[form_klass_name] = self.all_forms[form_klass_name]()

    def _instantiate_remaining_forms(self):
        for form_name in self.all_forms:
            if not isinstance(self.all_forms[form_name], (
                DeclarativeFieldsMetaclass, ModelFormMetaclass
            )):
                self._instantiate_model_form(form_name)

    def _initialize_existing_reg(self):
        self.action_type = 'edit'
        self.current_registration = get_object_or_404(
            RegDetails, pk=request.GET['reg_id']
        )
        self.conference = self.current_registration.conference
        try:
            crm_id = current_registration.registrant.crm_person.pk
            self.crm_match = Person.objects.get(pk=crm_id)
        except (AttributeError, Person.DoesNotExist):
            self.crm_match = None
        self._set_registrant(current_registration.registrant.pk)

    def _initialize_new_reg(self, request):
        self.action_type = 'new'
        self.current_registration = None
        self.conference = Event.objects.get(pk=request.GET['conf_id'])
        crm_id = request.GET.get('crm_id', None)
        registrant_id = request.GET.get('registrant_id', None)
        if registrant_id in ('', None) and crm_id not in ('', None):
            try:
                self.crm_match = Person.objects.get(pk=crm_id)
                if Registrants.objects.filter(crm_person=self.crm_match).exists():
                    registrant_id = Registrant.objects.filter(
                        crm_person=self.crm_match
                    )
            except Person.DoesNotExist:
                self.crm_match = None
        self._set_registrant(registrant_id)

    def _initialize_queued_reg(self, request):
        self.action_type = 'queue'
        self.current_registration = None
        self.queue_object = QueuedOrder.objects.get(pk=request.GET['queue_id'])
        self.conference = self.queue_object.conference
        self.crm_match = self.queue.object.crm_person
        self._set_registrant(request.GET.get('registrant_id'), None)

    def _main_setup(self):
        if self.action_type=='queue':
            reg_data = self._set_details_with_queued()
            self.data_source = 'queue'
        elif self.registrant is not None:
            reg_data = self._set_details_with_registrant()
            self.data_source = 'delegate'
        elif self.crm_person is not None:
            reg_data = self._set_details_with_crm_value()
            self.data_source = 'crm'
        else:
            reg_data = self._set_details_with_new()
            self.data_source = 'new'
        self._instantiate_model_form('reg_details_form', initial=reg_data)

    def _regdata_for_registration(self):
        if self.current_registration:
            reg_data = {
                'register_date': self.current_registration.register_date,
                'cancellation_date': self.current_registration.cancellation_date,
                'registration_status': self.current_registration.registration_status,
                'registration_notes': self.current_registration.registration_notes,
            }
            if hasattr(self.current_registration, 'invoice'):
                invoice = self.current_registration.invoice
                reg_data['sales_credit'] = invoice.sales_credit
                reg_data['pre_tax_price'] = invoice.pre_tax_price
                reg_data['gst_rate'] = invoice.gst_rate
                reg_data['hst_rate'] = invoice.hst_rate
                reg_data['qst_rate'] = invoice.qst_rate
                reg_data['payment_date'] = invoice.payment_date
                reg_data['payment_method'] = invoice.payment_method
                reg_data['fx_conversion_rate'] = invoice.fx_conversion_rate
                reg_data['invoice_notes'] = invoice.invoice_notes
                reg_data['sponsorship_description'] = invoice.sponsorship_description
            else:
                if self.company.gst_hst_exempt:
                    reg_data['gst_rate'] = 0
                    reg_data['hst_rate'] = 0
                if self.company.qst_exempt:
                    reg_data['qst_rate'] = 0
        else:
            reg_data = {}
            if self.company.gst_hst_exempt:
                reg_data['gst_rate'] = 0
                reg_data['hst_rate'] = 0
            if self.company.qst_exempt:
                reg_data['qst_rate'] = 0
            reg_data['sales_credit'] = None
        return reg_data

    def _set_conference_details(self):
        self.all_forms['options_form'] = OptionsForm(self.conference)
        self.all_forms['conference_select_form'] = ConferenceSelectForm(
            {'event': self.conference.pk }
        )

    def _set_details_with_registrant(self):
        # set company and company_select_form
        self.company = self.registrant.company
        self._instantiate_model_form('company_select_form',
                                     instance=self.company)
        # set assistant
        self.assistant = registrant.assistant
        # get data for new_delegate_form
        return self._regdata_for_registration()

    def _set_details_with_crm_value(self):
        # Set company and company_select_form
        self.company = None
        self._instantiate_model_form(
            'company_select_form',
            initial={
                'name': self.crm_match.company,
                'name_for_badges': self.crm_match.company[:30],
                'city': self.crm_match.city,
            }
        )
        # Set assistant
        self.assistant = None
        # get data for new_delegate_form
        # tokenize name into first_name/last_name guesses
        name_tokens = self.crm_match.name.split()
        if len(name_tokens) == 1:
            first_name_guess = ''
            last_name_guess = name_tokens[0]
        elif len(name_tokens) > 1:
            first_name_guess = name_tokens[0]
            last_name_guess = ' '.join(name_tokens[1:])
        else:
            first_name_guess = last_name_guess = ''
        # return dict for form's initial values
        return {
            'first_name': first_name_guess,
            'last_name': last_name_guess,
            'title': crm_match.title,
            'email1': crm_match.email,
            'email2': crm_match.email_alternate,
            'phone1': crm_match.phone,
            'phone2': crm_match.phone_alternate,
            'contact_option': 'D'
        }

    def _guess_company(self):
        company_list = Company.objects.filter(name=self.queue_object.name)
        if company_list.count() == 0:
            company_initial = {
                'name': self.queue_object.name,
                'name_for_badges': self.queue_object.name[:30],
                'address1': self.queue_object.address1,

            }

    def _set_details_with_queued(self):
        # try setting company
        if self.registrant:
            self.company = self.registrant.company
        else:
            self.company = self._guess_company()




        # set company and company_select_form
        self.company = None

        self._instantiate_model_form('company_select_form', instance=self.company, initial=None)

        # set assistant
        self.assistant = None

        # get data for new_delegate_form
        form_data = {}
        return form_data

    def _set_details_with_new(self):
        # Set company and company_select_form
        self.company = None
        self._instantiate_model_form('company_select_form')
        # Set assistant
        self.assistant = None
        # get data for new_delegate_form (empty dict)
        return {}

    def _set_initial(self, request):
        if 'reg_id' in request.GET:
            self._initialize_existing_reg()
        elif 'queue_id' in request.GET:
            self._initialize_queued_reg(request)
        elif 'conf_id' in request.GET:
            self._initialize_new_reg(request)
        else:
            return 'redirect'

    def _set_registrant(self, registrant_id):
        if registrant_id not in ('', None):
            self.registrant = Registrants.objects.get(pk=registrant_id)
            self.data_source = 'delegate'
            self._check_for_existing_regdetails()
        else:
            self.registrant = None
            self.current_registration = None

    def get(self, request, *args, **kwargs):
        # Initialize variables based on type of registration requested
        if self._set_initial(request) is not None:
            return redirect(self.redirect_url)
        # initialize forms that are the same no matter what
        self._set_conference_details()
        # set most of the rest of the details
        self._main_setup()

        # Instantiate any forms not yet instantiated
        self._instantiate_remaining_forms()
        return super(Index, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(Index, self).get_context_data(**kwargs)
        context['action_type'] = self.action_type
        context['conference'] = self.conference
        context['current_registration'] = self.current_registration
        context['registrant'] = self.registrant
        context['company'] = self.company
        context['conference_options'] = self.conference.eventoptions_set.all()
        context['queued_order_id'] = self.queued_order_id

        context['paid_status_values'] = PAID_STATUS_VALUES
        context['cxl_values'] = CXL_VALUES
        context['non_invoice_values'] = NON_INVOICE_VALUES
        context.update(self.all_forms)

        return context


@login_required
def index(request):
    """ renders base delegate/index.html page """
    action_type = 'new'
    if request.method == 'GET' and 'reg_id' in request.GET:
        try:
            current_registration = RegDetails.objects.get(
                pk=request.GET['reg_id']
            )
            action_type='edit'
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

        ## This is an ugly POS and very inefficient, but is a stopgap
        ## TODO: rework this whole view
        if registrant_id in ('', None) and crm_id != '':
            try:
                crm_match = Person.objects.get(pk=request.POST['crm_id'])
                if Registrants.objects.filter(crm_person=crm_match).exists():
                    registrant_id = Registrants.objects.filter(
                        crm_person=crm_match
                    )[0].pk
            except Person.DoesNotExist:
                pass

    else:
        conference = current_registration.conference
        conf_id = conference.pk
        try:
            crm_id = current_registration.registrant.crm_person.pk
        except AttributeError:
            crm_id = None
        registrant_id = current_registration.registrant.pk
        action_type = 'edit'
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
                action_type = 'edit'
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
                     'email2': crm_match.email_alternate,
                     'phone1': crm_match.phone,
                     'phone2': crm_match.phone_alternate,
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
        'conference_options': conference_options,
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
        'action_type': action_type,
    }
    return render(request, 'delegate/index.html', context)


class ProcessPayment(RegistrationPermissionMixin, FormView):
    model = RegDetails
    template_name = 'delegate/payment_details.html'
    success_url = reverse_lazy('delegate:confirmation_details')
    # http_method_names = ['post',]
    form_class = RegDetailsForm
    reg_details = None
    invoice = None
    event = None

    def _calculate_total_invoice(self):
        sub_total = self.invoice.pre_tax_price
        if self.invoice.hst_rate != 0:
            tax1 = sub_total * self.invoice.hst_rate
            pst = 0
            qst = 0
        else:
            tax1 = sub_total * self.invoice.gst_rate
            if qst != 0:
                qst = (sub_total + tax1) * self.invoice.qst_rate
                pst = 0
            else:
                qst = 0
                pst = sub_total * self.invoice.pst_rate
        total = sub_total + tax1 + qst + pst
        total = format(total, '.2f')
        return total

    def get(self, request, *args, **kwargs):
        try:
            self.reg_details = RegDetails.objects.get(
                pk=request.session['current_registration']
            )
        except KeyError:
            return redirect('/registration/')
        try:
            self.invoice = Invoice.objects.get(reg_details=self.reg_details)
        except Invoice.DoesNotExist:
            return HttpResponseRedirect(self.get_success_url())
        self.event = Event.objects.get(pk=self.reg_details.conference_id)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        overrides default
        """
        registrant = Registrants.objects.get(pk=self.request.session['registrant'])
        context = super(ProcessPayment, self).get_context_data(**kwargs)
        context['current_registration'] = self.reg_details
        context['invoice'] = self.invoice
        context['registrant'] = registrant
        context['total_invoice_amount'] = self._calculate_total_invoice()
        context['event'] = self.event
        return context

    def get_form_kwargs(self):
        """ Overrides default """
        kwargs = {
            'initial': self.get_initial(),
            'prefix': self.get_prefix(),
        }
        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        else:
            kwargs.update({
                'data': {
                    'registration_status': self.reg_details.registration_status,
                    'registration_notes': self.reg_details.registration_notes,
                    'payment_date': self.invoice.payment_date,
                    'invoice_notes': self.invoice.invoice_notes,
                    'payment_method': self.invoice.payment_method,
                    'pre_tax_price': self.invoice.pre_tax_price,
                    'gst_rate': self.invoice.gst_rate,
                    'hst_rate': self.invoice.hst_rate,
                    'qst_rate': self.invoice.qst_rate,
                }
            })
        return kwargs



class ProcessRegistration(RegistrationPermissionMixin,
                          ProcessCompleteRegistration, FormView):
    """
    Note - ChangeView mixin is necessary, but imported through
    ProcessCompleteRegistration
    """
    template_name = 'delegate/index.html'
    success_url = reverse_lazy('delegate:confirmation_details')
    payment_success_url = reverse_lazy('delegate:payment_details')
    http_method_names = ['post',]

    def _check_assistant_missing(self, request):
        if request.POST['contact_option'] in ('A', 'C') and not \
                request.POST['assistant_email']:
            self.assistant_missing = True
        else:
            self.assistant_missing = False

    def _check_integrity_errors(self, request):
        self._check_assistant_missing(request)
        self._check_option_selections(request)

    def _check_option_selections(self, request):
        self.option_list = []
        self.option_selection_needed = False
        if request.POST.getlist('event-option-selection'):
            for option in request.POST.getlist('event-option-selection'):
                self.option_list.append(EventOptions.objects.get(pk=option))
        if len(self.option_list) == 0 and \
                len(self.conference.eventoptions_set.all()) > 1:
            self.option_selection_needed = True
        elif len(self.option_list) == 0 and len(
            self.conference.eventoptions_set.all()
        ) == 1:
            self.option_list.append(self.conference.eventoptions_set.all()[0])

    def _everything_is_good(self):
        if self.new_delegate_form.is_valid() and \
                self.company_select_form.is_valid() and \
                (not self.has_assistant_data or
                 self.assistant_form.is_valid()) and \
                self.reg_details_form.is_valid() and \
                not self.company_error and \
                not self.assistant_missing and \
                not self.option_selection_needed and \
                self.conference:
            return True
        else:
            # print('\n\ninvalid\n')
            # print('new_delegate_form: ', self.new_delegate_form.is_valid())
            # print('company_select_form: ', self.company_select_form.is_valid())
            # print('assistant: ', (not self.has_assistant_data or self.assistant_form.is_valid()))
            # print('reg_details: ', self.reg_details_form.is_valid())
            # print('company_error: ', self.company_error)
            # print('assistant_missing: ', self.assistant_missing)
            # print('option_selection_needed: ', self.option_selection_needed)
            # print('conference: ', self.conference is not None)
            return False

    def _get_assistant_form(self, request):
        if (request.POST['assistant_first_name'] not in ('', None) or
            request.POST['assistant_last_name'] not in ('', None) or
            request.POST['assistant_title'] not in ('', None) or
            request.POST['assistant_email'] not in ('', None) or
            request.POST['assistant_phone'] not in ('', None)):
            self.has_assistant_data = True
            return AssistantForm({
                'salutation': request.POST['assistant_salutation'].strip(),
                'first_name': request.POST['assistant_first_name'].strip(),
                'last_name': request.POST['assistant_last_name'].strip(),
                'title': request.POST['assistant_title'].strip(),
                'email': request.POST['assistant_email'].strip(),
                'phone': request.POST['assistant_phone'].strip()
            })
        self.has_assistant_data = False
        return AssistantForm()

    def _get_reg_details_form(self, request):
        self.reg_details_data = {
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
                if 'sponsorship_description' in request.POST else None,
            'revised_flag': request.POST['revised_flag'] if 'revised_flag' in \
                request.POST else False
        }
        if request.POST['registration_status'] in NON_INVOICE_VALUES:
            self.reg_details_data['sales_credit'] = \
                self._get_valid_sales_rep_id(request)
        return RegDetailsForm(self.reg_details_data)

    def _get_valid_sales_rep_id(self, request):
        if request.user.groups.filter(name='sales').exists():
            return request.user.pk
        if request.user.groups.filter(name='sponsorship').exists():
            return request.user.pk
        if User.objects.filter(username__iexact='marketing').exists():
            return User.objects.filter(username__iexact='marketing')[0].pk
        return User.objects.filter(groups__name__iexact='sales')[0].pk

    def _set_assistant(self, request):
        if request.POST['assistant_match_value']:
            self.assistant = Assistant.objects.get(
                pk=request.POST['assistant_match_value']
            )
        else:
            self.assistant = None

    def _set_company(self, request):
        if request.POST['company_match_value'] not in ('new', ''):
            self.company = Company.objects.get(
                pk=request.POST['company_match_value']
            )
            self.company_error = False
        elif request.POST['company_match_value'] == 'new':
            if self.company_select_form.is_valid():
                self.company = self.company_select_form.save()
                self.company_error = False
            else:
                self.company = None
                self.company_error = True
        else:
            self.company = None
            self.company_error = True

    def _set_conference(self, request):
        if request.POST['selected_conference_id']:
            self.conference = Event.objects.get(
                pk=request.POST['selected_conference_id']
            )
        else:
            self.conference = None

    def _set_current_registration(self, request):
        if request.POST['current_regdetail_id']:
            self.current_registration = RegDetails.objects.get(
                pk=request.POST['current_regdetail_id']
            )
        else:
            self.current_registration = None

    def _set_crm_match(self, request):
        if request.POST['crm_match_value'] not in ('', 'new') and \
                not self.company_error:
            self.crm_match = Person.objects.get(
                pk=request.POST['crm_match_value']
            )
        else:
            if request.POST['crm_company'].strip() not in ('', None):
                crm_company_name = request.POST['crm_company'].strip()
            else:
                crm_company_name = request.POST['name'].strip()
            if self.company:
                crm_city = self.company.city
            elif request.POST['city'] not in ('', None):
                crm_city = request.POST['city']
            else:
                crm_city = ""
            self.crm_match = Person(
                name=request.POST['first_name'].strip() + ' ' + \
                     request.POST['last_name'].strip(),
                title=request.POST['title'].strip(),
                company=crm_company_name,
                phone=request.POST['phone1'].strip(),
                phone_alternate=request.POST['phone2'].strip(),
                email=request.POST['email1'].strip(),
                email_alternate=request.POST['email2'].strip(),
                city=crm_city,
                date_created=timezone.now(),
                created_by=request.user,
                date_modified=timezone.now(),
                modified_by=request.user,
            )
            if self.conference:
                if self.conference.default_dept:
                    self.crm_match.dept = self.conference.default_dept
                if self.conference.default_cat1:
                    self.crm_match.main_category = self.conference.default_cat1
                if self.conference.default_cat2:
                    self.crm_match.main_category2 = self.conference.default_cat2
            self.crm_match.save()
            self.add_change_record(self.crm_match, 'reg_add')

    def _set_registrant(self, request):
        if request.POST['current_registrant_id']:
            self.registrant = Registrants.objects.get(
                pk=request.POST['current_registrant_id']
            )
        else:
            self.registrant = None

    def _set_substitution_variables(self, request):
        self.action_type = request.POST['action_type']
        self.original_registrant = None
        if self.action_type == 'sub' and \
                request.POST['original_registrant_id'] not in ('', None):
            try:
                self.original_registrant = Registrants.objects.get(
                    pk=request.POST['original_registratnt_id']
                )
            except Registrants.DoesNotExist:
                pass

    def _set_variables(self, request):
        self._set_current_registration(request)
        self._set_substitution_variables(request)
        self._set_registrant(request)
        self._set_company(request)
        self._set_conference(request)
        self._set_crm_match(request)
        self._set_assistant(request)

    def form_invalid(self):
        """
        Override default
        """
        return self.render_to_response(self.get_context_data())

    def form_valid(self):
        """
        Overrides default (no form param)
        If the form is valid, redirect to the supplied URL.
        """
        return HttpResponseRedirect(self.get_success_url())

    def post(self, request, *args, **kwargs):
        self.new_delegate_form = self.get_form(form_class=NewDelegateForm)
        self.company_select_form = self.get_form(form_class=CompanySelectForm)
        self.assistant_form = self._get_assistant_form(request)
        self.reg_details_form = self._get_reg_details_form(request)
        self._set_variables(request)
        self._check_integrity_errors(request)
        if self._everything_is_good():
            self.process_complete_registration(request)
            return self.form_valid()
        else:
            return self.form_invalid()

    def get_context_data(self, **kwargs):
        """
        overrides default (doesn't include getting 'form')
        """
        # context = super(ProcessRegistration, self).get_context_data(**kwargs)
        context = kwargs
        if 'view' not in context:
            context['view'] = self

        context['new_delegate_form'] = self.new_delegate_form
        context['company_select_form'] = self.company_select_form
        context['assistant_form'] = self.assistant_form
        context['reg_details_form'] = self.reg_details_form

        context['current_registration'] = self.current_registration
        context['action_type'] = self.action_type
        context['original_registrant'] = self.original_registrant
        context['registrant'] = self.registrant
        context['company'] = self.company
        context['company_error'] = self.company_error  # DO I NEED THIS??
        context['conference'] = self.conference
        context['crm_match'] = self.crm_match
        context['assistant'] = self.assistant
        context['assistant_missing'] = self.assistant_missing
        context['option_selection_needed'] = self.option_selection_needed

        context['data_source'] = None  # CHECK THIS OUT
        context['company_match_list'] = None
        context['conference_options'] = self.conference.eventoptions_set.all()
        context['options_form'] = None
        context['crm_match_list'] = None
        context['new_company_form'] = NewCompanyForm()
        context['conference_select_form'] = ConferenceSelectForm()
        context['paid_status_values'] = PAID_STATUS_VALUES
        context['cxl_values'] = CXL_VALUES
        context['non_invoice_values'] = NON_INVOICE_VALUES

        return context

    def get_success_url(self):
        """
        Override default method to deal with 2 different options
        """
        submit_type = self.request.POST['submission_type']
        if submit_type == 'process-payment-button':
            if not self.payment_success_url:
                raise ImproperlyConfigured("No URL to redirect to.  Provide a payment_success_url.")
            return str(self.payment_success_url)
        if not self.success_url:
            raise ImproperlyConfigured("No URL to redirect to. Provide a success_url.")
        return str(self.success_url)  # success_url may be lazy



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


class CompanyCrmModal(RegistrationPermissionMixin, GuessCompanyMixin,
                      TemplateView):
    template_name = 'delegate/addins/company_crm_modal.html'

    def check_for_params(self):
        for param_name in ('company_id', 'crm_id', 'company_name', 'address1',
                           'address2', 'city', 'state_prov', 'city',
                           'state_prov', 'postal_code', 'first_name',
                           'last_name', 'title', 'email'):
            if param_name not in self.request.GET:
                raise Http404('Invalid Request: Missing param ' + param_name)

    def get(self, request, *args, **kwargs):
        self.check_for_params()
        return super(CompanyCrmModal, self).get(request, *args, **kwargs)

    def get_company(self):
        company_id = self.request.GET['company_id']
        if company_id == 'new':
            self.company = None
        elif company_id != '':
            try:
                self.company = Company.objects.get(pk=company_id)
            except Company.DoesNotExist:
                self.company = None
        else:
            self.company = None
        return self.company

    def get_crm_match(self):
        crm_id = self.request.GET['crm_id']
        if crm_id == 'new':
            self.crm_match = None
        elif crm_id != '':
            try:
                self.crm_match = Person.objects.get(pk=crm_id)
            except Person.DoesNotExist:
                self.crm_match = None
        else:
            self.crm_match = None
        return self.crm_match

    def get_context_data(self, **kwargs):
        context = super(CompanyCrmModal, self).get_context_data(**kwargs)
        context['company'] = self.get_company()
        context['crm_match'] = self.get_crm_match()
        context['company_best_guess'] = self.guess_company(self.request)
        context['company_suggest_list'] = self.company_suggest_list
        context['crm_best_guess'] = self.guess_crm(self.request)
        context['crm_suggest_list'] = self.crm_suggest_list
        context['have_suggestions'] = len(self.crm_suggest_list) + \
                len(self.company_suggest_list) > 0
        return context

    def guess_crm(self, request):
        """
        returns crm_best_guess and sets self.crm_suggest_list
        """
        # set empty variables to be returned if nothing found
        crm_best_guess = self.crm_match
        self.crm_suggest_list = []
        # skip this whole thing if we have a match already
        if self.crm_match:
            return

        # base variables
        crm_best_guess = self.crm_match
        self.crm_suggest_list = []
        name_tokens = request.GET['company_name'].strip().split()
        person_name = request.GET['first_name'].strip() + ' ' + \
                request.GET['last_name'].strip()
        email = request.GET['email'].strip()
        company_name = ' '.join(request.GET['company_name'].lower().strip().split())
        first_name = request.GET['first_name'].strip()
        last_name = request.GET['last_name'].strip()

        # Try to match on email
        if email not in ('', None):
            match1 = Person.objects.filter(email=email)
        else:
            match1 = Person.objects.none()
        match0 = Person.objects.none()
        if match1.count() == 1:
            crm_best_guess = match1[0]
        # deal with case where more than one Person matches on email
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
                crm_best_guess = match1[0]
        self.crm_suggest_list = match0 | match1
        # Only proceed if we have fewer than 10 suggestions
        if self.crm_suggest_list.count() > 9:
            return crm_best_guess

        # match on name and company
        match2 = Person.objects.filter(name=person_name,
                                       company=company_name)
        if not crm_best_guess and match2.count() > 0:
            crm_best_guess = match2[0]
        self.crm_suggest_list = self.crm_suggest_list | match2
        # only proceed if we have fewer than 10 suggestions
        if self.crm_suggest_list.count() > 9:
            return crm_best_guess

        # match on either first or last name and company name
        name_qs1 = Person.objects.filter(name__icontains=first_name,
                                         company=company_name)
        name_qs2 = Person.objects.filter(name__icontains=last_name,
                                         company=company_name)
        self.crm_suggest_list = self.crm_suggest_list | name_qs1 | name_qs2
        # only proceed if we have fewer than 10 suggestions and company name
        if self.crm_suggest_list.count() > 9 or len(name_tokens) == 0:
            return crm_best_guess

        # match on full name and company tokens
        match3 = Person.objects.filter(name=person_name)
        queries = []
        for token in name_tokens:
            queries.append(Q(company__icontains=token))
        query = queries.pop()
        for item in queries:
            query |= item
        match3 = match3.filter(query)
        if match3.count() > 9:
            self.crm_suggest_list = list(set(list(self.crm_suggest_list) +
                                             list(match3[:10])))
        else:
            self.crm_suggest_list = self.crm_suggest_list | match3
        # only proceed if we have fewer than 10 suggestions
        if self.crm_suggest_list.count() > 9:
            return crm_best_guess

        match4a = Person.objects.filter(name__icontains=first_name)
        match4b = Person.objects.filter(name__icontains=last_name)
        match4 = match4a | match4b
        match4 = match4.filter(company__icontains=company_name)
        if match4.count() > 9:
            self.crm_suggest_lsit = list(set(list(self.crm_suggest_list) +
                                             list(match4[:10])))
        else:
            self.crm_suggest_list = self.crm_suggest_list | match4
        return crm_best_guess


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
    company_suggest_list = None
    crm_suggest_list = None
    company_best_guess = None  # This is a company object or None
    crm_best_guess = None  # This is a person object or None
    if request.POST['company_id'] == 'new':
        company = None
    elif request.POST['company_id'] != '':
        try:
            company = Company.objects.get(pk=request.POST['company_id'])
        except Company.DoesNotExist:
            company = None
    else:
        company = None
    if request.POST['crm_id'] == 'new':
        crm_match = None
    elif request.POST['crm_id'] != '':
        try:
            crm_match = Person.objects.get(pk=request.POST['crm_id'])
        except Person.DoesNotExist:
            crm_match = None
    else:
        crm_match = None
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
        if crm_suggest_list.count() < 10 and len(name_tokens) > 0:
            match3 = Person.objects.filter(name=person_name)
            queries = []
            for token in name_tokens:
                queries.append(Q(company__icontains=token))
            query = queries.pop()
            for item in queries:
                query |= item
            match3 = match3.filter(query)
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
        company_data['company_name'] = company_data.pop('name')
    else:
        company_data = {'id': None}
    return JsonResponse(company_data)


@login_required
def get_substitute_details(request):
    """
    called from substitute_match_list.html (modal)
    returns JSON of details of subtitute to be inserted into index.html
    """
    if 'sub_type' not in request.GET or (
        request.GET['sub_type'] in ['crm', 'del']
        and 'sub_id' not in request.GET
    ):
        raise Http404('Substitute not specified')
    if 'orig_del' not in request.GET:
        raise Http404('Original delegate not specified')
    orig_del = get_object_or_404(Registrants, pk=request.GET['orig_del'])
    if request.GET['sub_type'] == 'crm':
        crm_sub = get_object_or_404(Person, pk=request.GET['sub_id'])
        name_tokens = crm_sub.name.split()
        if len(name_tokens) > 1:
            first_name = name_tokens[0]
            last_name = ' '.join(name_tokens[1:])
        elif len(name_tokens) == 1:
            first_name = name_tokens[0]
            last_name = ''
        else:
            first_name = ''
            last_name = ''
        try:
            assistant_id = orig_del.assistant.pk
            assistant_salutation = orig_del.assistant.salutation
            assistant_first_name = orig_del.assistant.first_name
            assistant_last_name = orig_del.assistant.last_name
            assistant_title = orig_del.assistant.title
            assistant_email = orig_del.assistant.email
            assistant_phone = orig_del.assistant.phone
        except (Assistant.DoesNotExist, AttributeError):
            assistant_id = None
            assistant_salutation = None
            assistant_first_name = None
            assistant_last_name = None
            assistant_title = None
            assistant_email = None
            assistant_phone = None
        sub_details = {
            'newRegistrantId': None,
            'newCrmId': crm_sub.pk,
            'salutation': None,
            'firstName': first_name,
            'lastName': last_name,
            'title': crm_sub.title,
            'email1': crm_sub.email,
            'email2': None,
            'phone1': crm_sub.phone,
            'phone2': None,
            'asstId': assistant_id,
            'asstSalutation': assistant_salutation,
            'asstFirstName': assistant_first_name,
            'asstLastName': assistant_last_name,
            'asstTitle': assistant_title,
            'asstEmail': assistant_email,
            'asstPhone': assistant_phone,
        }
    elif request.GET['sub_type'] == 'del':
        del_sub = get_object_or_404(Registrants, pk=request.GET['sub_id'])
        try:
            assistant_id = del_sub.assistant.pk
            assistant_salutation = del_sub.assistant.salutation
            assistant_first_name = del_sub.assistant.first_name
            assistant_last_name = del_sub.assistant.last_name
            assistant_title = del_sub.assistant.title
            assistant_email = del_sub.assistant.email
            assistant_phone = del_sub.assistant.phone
        except (Assistant.DoesNotExist, AttributeError):
            assistant_id = None
            assistant_salutation = None
            assistant_first_name = None
            assistant_last_name = None
            assistant_title = None
            assistant_email = None
            assistant_phone = None
        sub_details = {
            'newRegistrantId': del_sub.pk,
            'newCrmId': del_sub.crm_person.pk,
            'salutation': del_sub.salutation,
            'firstName': del_sub.first_name,
            'lastName': del_sub.last_name,
            'title': del_sub.title,
            'email1': del_sub.email1,
            'email2': del_sub.email2,
            'phone1': del_sub.phone1,
            'phone2': del_sub.phone2,
            'asstId': assistant_id,
            'asstSal': assistant_salutation,
            'asstFirstName': assistant_first_name,
            'asstLastName': assistant_last_name,
            'asstTitle': assistant_title,
            'asstEmail': assistant_email,
            'asstPhone': assistant_phone,
        }
    else:  # Assume it's a new delegate
        sub_details = {
            'newRegistrantId': None,
            'newCrmId': None,
            'salutation': None,
            'firstName': None,
            'lastName': None,
            'title': None,
            'email1': None,
            'email2': None,
            'phone1': None,
            'phone2': None,
            'asstId': None,
            'asstSal': None,
            'asstFirstName': None,
            'asstLastName': None,
            'asstTitle': None,
            'asstEmail': None,
            'asstPhone': None,
        }
    return JsonResponse(sub_details)


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
    if set(('conf_id', 'first_name', 'last_name', 'company_id',
            'current_registrant')) > request.GET.keys():
        return HttpResponse('')
    try:
        conference = Event.objects.get(pk=request.GET['conf_id'])
    except Event.DoesNotExist:
        raise Http404('Conference does not exist')
    try:
        company = Company.objects.get(pk=request.GET['company_id'])
    except Company.DoesNotExist:
        raise Http404('Company does not exist')
    try:
        registrant = Registrants.objects.get(
            pk=request.GET['current_registrant']
        )
    except Registrants.DoesNotExist:
        raise Http404('Delegate does not exist')
    # Search for registrant in same company
    registrant_list = []
    reg_query1 = Registrants.objects.filter(
        first_name__icontains=request.GET['first_name'].strip(),
        last_name__icontains=request.GET['last_name'].strip(),
        company=company
    ).order_by('last_name', 'first_name').exclude(pk=registrant.pk)
    registrant_list.extend(list(reg_query1))
    reg_query2 = Registrants.objects.filter(
        first_name__icontains=request.GET['first_name'].strip(),
        last_name__icontains=request.GET['last_name'].strip(),
        company__name__icontains=company.name.strip(),
    ).exclude(id__in=reg_query1).order_by('last_name', 'first_name').exclude(
        pk=registrant.pk
    )
    registrant_list.extend(list(reg_query2))
    # search for soft matches
    company_soft_match1 = iteratively_replace_and_guess_name(company.name)
    reg_query3 = Registrants.objects.filter(
        first_name__icontains=request.GET['first_name'].strip(),
        last_name__icontains=request.GET['last_name'].strip(),
        company__in=company_soft_match1
    ).exclude(id__in=reg_query1).exclude(id__in=reg_query2).order_by(
        'last_name', 'first_name'
    ).exclude(pk=registrant.pk)
    registrant_list.extend(list(reg_query3))
    company_soft_match2 = guess_by_ngrams(company.name)
    reg_query4 = Registrants.objects.filter(
        first_name__icontains=request.GET['first_name'].strip(),
        last_name__icontains=request.GET['last_name'].strip(),
        company__in=company_soft_match2
    ).exclude(id__in=reg_query1).exclude(id__in=reg_query2).exclude(
        id__in=reg_query3
    ).order_by('last_name', 'first_name').exclude(pk=registrant.pk)
    registrant_list.extend(list(reg_query4))


    # Search for matching CRM records
    crm_list = []
    crm_query1 = Person.objects.filter(
        Q(name__icontains=request.GET['first_name'].strip()) &
        Q(name__icontains=request.GET['last_name'].strip()) &
        Q(company__icontains=company.name.strip())
    )
    crm_list.extend(list(crm_query1))
    soft_match_list1 = company_soft_match1.values_list('name',
                                                       flat=True).distinct()
    soft_match_list2 = company_soft_match2.values_list('name',
                                                       flat=True).distinct()
    if crm_query1.count() < 10:
        if request.GET['last_name'] != '' and request.GET['first_name'] != '':
            crm_query2 = Person.objects.filter(
                (Q(name__icontains=request.GET['first_name'].strip()) |
                 Q(name__icontains=request.GET['last_name'].strip())) &
                Q(company__icontains=company.name.strip())
            ).exclude(id__in=crm_query1)
            crm_query3 = Person.objects.filter(
                (Q(name__icontains=request.GET['first_name'].strip()) |
                 Q(name__icontains=request.GET['last_name'].strip())) &
                Q(company__in=soft_match_list1)  # mySQL queryset case insensitive
            ).exclude(id__in=crm_query1).exclude(id__in=crm_query2)
            crm_query4 = Person.objects.filter(
                (Q(name__icontains=request.GET['first_name'].strip()) |
                 Q(name__icontains=request.GET['last_name'].strip())) &
                Q(company__in=soft_match_list2)
            ).exclude(id__in=crm_query1).exclude(
                id__in=crm_query2
            ).exclude(id__in=crm_query3)
        elif request.GET['last_name'] == '' and request.GET['first_name'] != '':
            crm_query2 = Person.objects.filter(
                Q(name__icontains=request.GET['first_name'].strip()) &
                Q(company__icontains=company.name.strip())
            ).exclude(id__in=crm_query1)
            crm_query3 = Person.objects.filter(
                Q(name__icontains=request.GET['first_name'].strip()) &
                Q(company__in=soft_match_list1)
            ).exclude(id__in=crm_query1).exclude(id__in=crm_query2)
            crm_query4 = Person.objects.filter(
                Q(name__icontains=request.GET['first_name'].strip()) &
                Q(company__in=soft_match_list2)
            ).exclude(id__in=crm_query1).exclude(
                id__in=crm_query2
            ).exclude(id__in=crm_query3)
        elif request.GET['last_name'] != '' and request.GET['first_name'] == '':
            crm_query2 = Person.objects.filter(
                Q(name__icontains=request.GET['last_name'].strip()) &
                Q(company__icontains=company.name.strip())
            ).exclude(id__in=crm_query1)
            crm_query3 = Person.objects.filter(
                Q(name__icontains=request.GET['last_name'].strip()) &
                Q(company__in=soft_match_list1)
            ).exclude(id__in=crm_query1).exclude(id__in=crm_query2)
            crm_query4 = Person.objects.filter(
                Q(name__icontains=request.GET['last_name'].strip()) &
                Q(company__in=soft_match_list2)
            ).exclude(id__in=crm_query1).exclude(
                id__in=crm_query2
            ).exclude(id__in=crm_query3)
        else:
            crm_query2 = Person.objects.none()
            crm_query3 = Person.objects.none()
            crm_query4 = Person.objects.none()

        crm_list.extend(list(crm_query2))
        if len(crm_list) < 15:
            crm_list.extend(list(crm_query3))
        if len(crm_list) < 15:
            crm_list.extend(list(crm_query4))

    context = {
        'registrant_list': registrant_list,
        'conference': conference,
        'crm_list': crm_list,
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
def suggest_assistant_data(request):
    query_term = request.GET.get('q', '')
    suggest_field = request.GET.get('f', '')
    if suggest_field == 'first_name':
        selects = Assistant.objects.filter(
            first_name__icontains=query_term
        ).values('first_name').annotate(
            total=Count('first_name')
        ).order_by('-total')[:25]
    elif suggest_field == 'last_name':
        selects = Assistant.objects.filter(
            last_name__icontains=query_term
        ).values('last_name').annotate(
            total=Count('last_name')
        ).order_by('-total')[:25]
    elif suggest_field == 'email':
        selects = Assistant.objects.filter(
            email__icontains=query_term
        ).values('email').annotate(
            total=Count('email')
        ).order_by('-total')[:25]
    elif suggest_field == 'title':
        selects = Assistant.objects.filter(
            title__icontains=query_term
        ).values('title').annotate(
            total=Count('title')
        ).order_by('-total')[:25]
    elif suggest_field == 'phone':
        selects = Assistant.objects.filter(
            phone__icontains=query_term
        ).values('phone').annotate(
            total=Count('phone')
        ).order_by('-total')[:25]
    else:
        selects = None
    results = []
    if selects:
        for select in selects:
            select_json = {}
            select_json['identifier'] = select[suggest_field]
            results.append(select_json)
    data = json.dumps(results)
    mimetype = 'applications/json'
    return HttpResponse(data, mimetype)


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
            try:
                if current_reg.invoice:
                    # form_data['sponsorship_description'] = \
                    #     current_reg.invoice.sponsorship_description
                    form_data['payment_date'] = current_reg.invoice.payment_date
                    form_data['payment_method'] = \
                        current_reg.invoice.payment_method
                    reg_details_form = RegDetailsForm(
                        form_data, instance=current_reg.invoice
                    )
            except Invoice.DoesNotExist:
                reg_details_form = RegDetailsForm(form_data)
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
    else:
        pdf = None

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
    email.send()
    return HttpResponse(status=204)
