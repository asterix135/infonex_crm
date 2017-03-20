import csv
from io import BytesIO
import json
from openpyxl import Workbook

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.template import RequestContext
from django.urls import reverse
from django.utils import timezone
from django.utils.datastructures import MultiValueDictKeyError

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate

from .forms import *
from .models import *
from .pdfs import *
from crm.models import Person, Event
from delegate.constants import *

########################
# HELPER FUNCTIONS
########################
def create_temp_conf_number():
    """ helper function for add_event_option """
    base_number = "TEMP"
    counter = 0
    while True:
        event_number = base_number + str(counter)
        if Event.objects.filter(number=event_number).count() == 0:
            return event_number
        counter += 1


########################
# BASE VIEWS
########################
@login_required
def add_edit_conference(request):
    """ Renders conference page """
    edit_action = 'blank'
    event = None
    event_option_set = None
    conference_edit_form = ConferenceEditForm()
    conference_option_form = ConferenceOptionForm()
    if request.method == 'GET':
        edit_action = request.GET.get('action', 'blank')
        if edit_action not in ('blank', 'new', 'edit'):
            edit_action = 'blank'
        if edit_action == 'edit':
            try:
                event = Event.objects.get(pk=request.GET['id'])
                conference_edit_form = ConferenceEditForm(instance=event)
                event_option_set = event.eventoptions_set.all()
            except (Event.DoesNotExist, MultiValueDictKeyError):
                edit_action = 'blank'

    venue_list = Venue.objects.all().order_by('city', 'name')
    venue_form = VenueForm()
    conference_select_form = ConferenceSelectForm()
    context = {
        'edit_action': edit_action,
        'venue_form': venue_form,
        'venue_list': venue_list,
        'conference_select_form': conference_select_form,
        'conference_edit_form': conference_edit_form,
        'conference_option_form': conference_option_form,
        'event': event,
        'event_option_set': event_option_set,
    }
    return render(request, 'registration/conference.html', context)


@login_required
def index(request):
    return render(request, 'registration/index.html')


@login_required
def new_delegate_search(request):
    """ Renders new_delegate_search page"""
    if request.method == 'POST':
        person_form = NewDelegateSearchForm(request.POST)
        if (request.POST['first_name'] == '' and
            request.POST['last_name'] == '' and
            request.POST['company'] == '' and
            request.POST['postal_code'] == '' and
            # TODO: This probably should be changed until event search
            # functionality is enabled
            request.POST['event'] == ''):

            past_customer_list = None
            crm_list = None
            search_entered = True
        else:
            filterargs = {
                'first_name__icontains': request.POST['first_name'],
                'last_name__icontains': request.POST['last_name'],
                'company__name__icontains': request.POST['company'],
                'company__postal_code__icontains': request.POST['postal_code'],
            }
            if request.POST['event'] != '':
                filterargs['regdetails__conference__pk'] = request.POST['event']
            past_customer_list = Registrants.objects.filter(**filterargs)

            crm_list = Person.objects.filter(
                Q(name__icontains=request.POST['first_name']) &
                Q(name__icontains=request.POST['last_name']),
                Q(company__icontains=request.POST['company'])
            ).order_by('company', 'name')[:100]
            search_entered = True
    else:
        person_form = NewDelegateSearchForm()
        past_customer_list = None
        crm_list = None
        search_entered = None
    context = {
        'person_form': person_form,
        'past_customer_list': past_customer_list,
        'crm_list': crm_list,
        'search_entered': search_entered,
    }
    return render(request, 'registration/new_delegate_search.html', context)


#######################
# AJAX CALLS
#######################
@login_required
def add_event_option(request):
    """ ajax call to add options to a conference """
    conference_option_form = ConferenceOptionForm()
    event_option_set = None
    event = None
    if request.method == 'POST':
        try:
            event_id = request.POST['event_id']
        except MultiValueDictKeyError:
            event_id = None
        conference_option_form = ConferenceOptionForm(request.POST)
        if conference_option_form.is_valid():
            if not event_id:
                new_event_number = create_temp_conf_number()
                event = Event(
                    number=new_event_number,
                    title='Placeholder Event',
                    city='Placeholder City',
                    date_begins=timezone.now(),
                    registrar=request.user,
                    state_prov='ON',
                    created_by=request.user,
                    modified_by=request.user,
                )
                event.save()
            else:
                event = Event.objects.get(pk=event_id)
            option = EventOptions(
                event=event,
                name=request.POST['name'],
                startdate=request.POST['startdate'],
                enddate=request.POST['enddate'],
                primary=True if request.POST['primary'] == 'true' else False,
            )
            option.save()
            conference_option_form = ConferenceOptionForm()
            event_option_set = event.eventoptions_set.all()
        else:
            if event_id:
                event = Event.objects.get(pk=event_id)
                event_option_set = event.eventoptions_set.all()
    context = {
        'conference_option_form': conference_option_form,
        'event_option_set': event_option_set,
        'event': event,
    }
    return render(request, 'registration/addins/conference_options_panel.html',
                  context)


@login_required
def add_venue(request):
    """ AJAX Function to add new venue and refresh venue sidebar """
    errors = False
    venue_list = Venue.objects.all().order_by('city', 'name')
    if request.method == 'POST':
        venue_form = VenueForm(request.POST)
        errors = True
        if venue_form.is_valid():
            errors = False
            venue_form.save()
            venue_form = VenueForm()
    else:
        venue_form = VenueForm()
    context = {
        'venue_form': venue_form,
        'venue_list': venue_list,
        'errors': errors,
    }
    return render(request, 'registration/addins/venue_sidebar.html', context)


@login_required
def delete_event_option(request):
    """ ajax call to delete option from a conference """
    conference_option_form = ConferenceOptionForm()
    event_option_set = None
    event = None
    if request.method == 'POST':
        try:
            event_id = request.POST['event_id']
            event = Event.objects.get(pk=event_id)
        except (MultiValueDictKeyError, Event.DoesNotExist):
            event_id = None
        try:
            option_id = request.POST['option_id']
            option = EventOptions.objects.get(pk=option_id)
        except (EventOptions.DoesNotExist, MultiValueDictKeyError):
            option_id = None
        if event_id and option_id:
            option.delete()
            event_option_set = event.eventoptions_set.all()
    context = {
        'conference_option_form': conference_option_form,
        'event_option_set': event_option_set,
        'event': event,
    }
    return render(request, 'registration/addins/conference_options_panel.html',
                  context)


@login_required
def delete_temp_conf(request):
    """ ajax call to delete temporary conference and options """
    event = None
    if request.method == 'POST':
        try:
            event = Event.objects.get(pk=request.POST['event_id'])
        except (Event.DoesNotExist, MultiValueDictKeyError):
            event = None
        if event:
            event.delete()
    return HttpResponse('')


@login_required
def delete_venue(request):
    """ AJAX function to delete venue """
    venue_form = VenueForm()
    # TODO: Update this when filter function implemented
    venue_list = Venue.objects.all().order_by('city', 'name')
    if request.method == 'POST' and 'venue_id' in request.POST:
        try:
            venue = Venue.objects.get(id=request.POST['venue_id'])
        except (Venue.DoesNotExist, MultiValueDictKeyError):
            venue = None
        if venue:
            venue.delete()
    context = {
        'venue_form': venue_form,
        'venue_list': venue_list,
    }
    return render(request, 'registration/addins/venue_sidebar.html', context)


@login_required
def edit_venue(request):
    """ AJAX function to edit venue information in sidebar """
    venue = None
    venue_id = None
    template = 'registration/addins/venue_detail.html'
    if request.method == 'GET':
        venue_id = request.GET['id']
    elif request.method == 'POST':
        venue_id = request.POST['id']
    if venue_id:
        venue = Venue.objects.get(pk=venue_id)
        if request.method == 'GET':
            venue_form = VenueForm(instance=venue)
            template = 'registration/addins/venue_edit.html'
        elif request.method == 'POST':
            venue_form = VenueForm(request.POST, instance=venue)
            if venue_form.is_valid():
                venue_form.save()
            else:
                template = 'registration/addins/venue_edit.html'
        else:
            venue_form = VenueForm()

    context = {'venue': venue,
               'venue_form': venue_form,}
    return render(request, template, context)


@login_required
def filter_venue(request):
    """
    Dynamically filter list of venues based on city
    """
    venue_form = VenueForm()
    try:
        city_partial = request.GET['city_partial']
        venue_list = Venue.objects.filter(
            city__icontains=city_partial).order_by('city', 'name')
    except MultiValueDictKeyError:
        city_partial = None
        venue_list = Venue.objects.all().order_by('city', 'name')
    context = {
        'venue_form': venue_form,
        'venue_list': venue_list,
    }
    return render(request, 'registration/addins/venue_sidebar.html', context)


@login_required
def get_registration_history(request):
    """AJAX call to get reg history for past delegate"""
    context = RequestContext(request)
    person_id = None
    person_regs = None
    if request.method == 'GET':
        person_id = request.GET['id']
    if person_id:
        person = Registrants.objects.get(pk=person_id)
        person_regs = person.regdetails_set.all()
    return render(request, 'registration/addins/reg_history.html',
        {'person_regs': person_regs})


@login_required
def index_panel(request):
    if 'panel' not in request.GET:
        return HttpResponse('')
    if request.GET['panel'] == 'admin-reports':
        response_url = 'registration/index_panels/admin_reports.html'
        conference_select_form = ConferenceSelectForm()
        conference_select_form.fields['event'].queryset = \
            Event.objects.all().order_by('-date_begins')
        admin_report_options_form = AdminReportOptionsForm()
        context = {
            'conference_select_form': conference_select_form,
            'admin_report_options_form': admin_report_options_form,
        }
    elif request.GET['panel'] == 'reg-search':
        response_url = 'registration/index_panels/registration_search.html'
        delegate_search_form = NewDelegateSearchForm()
        delegate_search_form.fields['event'].queryset = \
            Event.objects.all().order_by('-date_begins')
        context = {
            'delegate_search_form': delegate_search_form,
        }

    else:
        raise Http404('Invalid panel name')

    return render(request, response_url, context)


@login_required
def save_conference_changes(request):
    """ AJAX call to save changes to conference being edited """
    event = None
    edit_action = None
    conference_option_form = ConferenceOptionForm()
    conference_edit_form = ConferenceEditForm()
    event_option_set = None
    if request.method == 'POST':
        try:
            event_id = request.POST['event_id']
            if event_id != 'new':
                event = Event.objects.get(pk=event_id)
            conference_edit_form = ConferenceEditForm(
                request.POST, instance=event
            )
            if conference_edit_form.is_valid():
                event = conference_edit_form.save()
                return HttpResponse('')
        except (Event.DoesNotExist, MultiValueDictKeyError):
            conference_edit_form = ConferenceEditForm(request.POST)
    context = {
        'edit_action': edit_action,
        'conference_edit_form': conference_edit_form,
        'conference_option_form': conference_option_form,
        'event': event,
        'event_option_set': event_option_set,
    }
    return render(request, 'registration/addins/conference_edit_panel.html',
                  context)


@login_required
def search_dels(request):
    """
    AJAX call to get matching delegates and crm contacts for new_delegate_search
    """
    if request.method == 'POST':
        if (request.POST['first_name'] == '' and
            request.POST['last_name'] == '' and
            request.POST['company'] == '' and
            request.POST['postal_code'] == ''):

            past_customer_list = None
            crm_list = None
            search_entered = True
            conference = None
        else:
            filterargs = {
                'first_name__icontains': request.POST['first_name'],
                'last_name__icontains': request.POST['last_name'],
                'company__name__icontains': request.POST['company'],
                'company__postal_code__icontains': request.POST['postal_code'],
            }
            past_customer_list = Registrants.objects.filter(**filterargs)
            crm_list = Person.objects.filter(
                Q(name__icontains=request.POST['first_name']) &
                Q(name__icontains=request.POST['last_name']),
                Q(company__icontains=request.POST['company'])
            ).order_by('company', 'name')[:100]
            search_entered = True
            try:
                conference = Event.objects.get(pk=request.POST['event'])
            except (ValueError, Event.DoesNotExist):
                conference = None
    else:
        past_customer_list = None
        crm_list = None
        search_entered = None
        conference = None
    context = {
        'past_customer_list': past_customer_list,
        'crm_list': crm_list,
        'search_entered': search_entered,
        'conference': conference,
    }
    return render(request, 'registration/addins/match_del_list.html', context)


@login_required
def select_conference_to_edit(request):
    """ ajax call to select conference for editing """
    event = None
    edit_action = 'new'
    conference_edit_form = ConferenceEditForm()
    conference_option_form = ConferenceOptionForm()
    event_option_set = None
    if request.method == 'POST':
        if request.POST['edit_action'] != 'edit':
            edit_action = 'blank'
        else:
            try:
                event = Event.objects.get(pk=request.POST['conf_id'])
                edit_action = 'edit'
                conference_edit_form = ConferenceEditForm(instance=event)
                event_option_set = event.eventoptions_set.all()
            except (Event.DoesNotExist, MultiValueDictKeyError):
                edit_action = 'blank'
    context = {
        'edit_action': edit_action,
        'conference_edit_form': conference_edit_form,
        'conference_option_form': conference_option_form,
        'event': event,
        'event_option_set': event_option_set,
    }
    return render(request, 'registration/addins/conference_edit_panel.html',
                  context)


@login_required
def suggest_first_name(request):
    """
    Ajax call - returns json of top 25 first names (by number in db) that
    match entered string
    """
    query_term = request.GET.get('q', '')
    selects = Registrants.objects.filter(first_name__icontains=query_term) \
        .values('first_name').annotate(total=Count('first_name')) \
        .order_by('-total')[:25]
    results = []
    for select in selects:
        select_json = {}
        select_json['identifier'] = select['first_name']
        results.append(select_json)
    data = json.dumps(results)
    mimetype = 'applications/json'
    return HttpResponse(data, mimetype)


@login_required
def suggest_last_name(request):
    """
    Ajax call - returns json of top 25 first names (by number in db) that
    match entered string
    """
    query_term = request.GET.get('q', '')
    selects = Registrants.objects.filter(last_name__icontains=query_term) \
        .values('last_name').annotate(total=Count('last_name')) \
        .order_by('-total')[:25]
    results = []
    for select in selects:
        select_json = {}
        select_json['identifier'] = select['last_name']
        results.append(select_json)
    data = json.dumps(results)
    mimetype = 'applications/json'
    return HttpResponse(data, mimetype)


@login_required
def unfilter_venue(request):
    """
    AJAX Call
    """
    venue_form = VenueForm()
    venue_list = Venue.objects.all().order_by('city', 'name')
    context = {
        'venue_form': venue_form,
        'venue_list': venue_list,
    }
    return render(request, 'registration/addins/venue_sidebar.html', context)


@login_required
def update_conference_choices(request):
    """ ajax call to update conference select dropdown on conference.html """
    conference_select_form = ConferenceSelectForm()
    return render(request,
                  'registration/addins/conference_select_dropdown.html',
                  {'conference_select_form': conference_select_form})


@login_required
def update_venue_choices(request):
    """ ajax call to update venue selection choices dropdown when new venue added """
    conference_edit_form = ConferenceEditForm()
    return render(request, 'registration/addins/conference_venue_choices.html',
                  {'conference_edit_form': conference_edit_form})


############################
# GRAPHICS/DOCUMENTS
############################
@login_required
def get_admin_reports(request):
    # Pull relevant info out of GET request
    if 'event' not in request.GET:
        raise Http404('Event not specified')
    event = get_object_or_404(Event, pk=request.GET['event'])
    sort = request.GET.get('sort', 'company')
    if sort not in ('company', 'name', 'title'):
        sort = 'company'
    destination = request.GET.get('destination', 'inline')
    if destination not in ('attachment', 'inline'):
        destination = 'attachment'
    doc_format = request.GET.get('doc_format', 'pdf')
    if doc_format not in ('pdf', 'csv', 'xlsx'):
        doc_format = 'pdf'
    report_type = request.GET.get('report', '')
    sort_orders = {
        'name': ['registrant__last_name',
                 'registrant__first_name',
                 'registrant__company__name'],
        'title': ['registrant__title',
                  'registrant__company__name',
                  'registrant__last_name',
                  'registrant__first_name'],
        'company': ['registrant__company__name',
                    'registrant__title',
                    'registrant__last_name',
                    'registrant__first_name']
    }

    if doc_format == 'pdf':
        buffr = BytesIO()
        report = ConferenceReportPdf(buffr, event, sort)
        response = HttpResponse(content_type='application/pdf')
        if report_type == 'Delegate':
            file_details = destination + '; filename="delegate_list_' + \
                str(event.number) + '.pdf"'
            response['Content-Disposition'] = file_details
            pdf = report.generate_delegate_list()
        elif report_type == 'NoName':
            file_details = destination + '; filename="delegate_list_' + \
                str(event.number) + '.pdf"'
            response['Content-Disposition'] = file_details
            pdf = report.generate_no_name_list()
        elif report_type == 'Registration':
            file_details = destination + '; filename="registration_list_' + \
                str(event.number) + '.pdf"'
            response['Content-Disposition'] = file_details
            pdf = report.generate_registration_list()
        elif report_type == 'Phone':
            file_details = destination + '; filename="phone_list_' + \
                str(event.number) + '.pdf"'
            response['Content-Disposition'] = file_details
            pdf = report.generate_phone_list()
        elif report_type == 'Onsite':
            file_details = destination + '; filename="onsite_delegate_list_' + \
                str(event.number) + '.pdf"'
            response['Content-Disposition'] = file_details
            pdf = report.generate_onsite_list()
        elif report_type == 'Unpaid':
            file_details = destination + '; filename="unpaid_delegate_list_' + \
                str(event.number) + '.pdf"'
            response['Content-Disposition'] = file_details
            pdf = report.generate_unpaid_list()
        elif report_type == 'CE':
            file_details = destination + '; filename="CE_signin_' + \
                str(event.number) + '.pdf"'
            response['Content-Disposition'] = file_details
            pdf = report.generate_ce_sign_in_sheet()
        elif report_type == 'Badges':
            file_details = destination + '; filename="badges_' + \
                str(event.number) + '.pdf"'
            response['Content-Disposition'] = file_details
            pdf = report.badges()
        elif report_type == 'Counts':
            file_details = destination + '; filename="count_report_' + \
                str(event.number) + '.pdf"'
            response['Content-Disposotion'] = file_details
            pdf = report.delegate_count()
        else:  # Invalid report type
            buffr.close()
            raise Http404('Invalid report type')
        buffr.close()
        response.write(pdf)
        return response
    elif doc_format == 'csv':
        response = HttpResponse(content_type='text/csv')

        if report_type == 'Delegate':
            file_details = destination + '; filename="delegate_list_' + \
                str(event.number) + '.csv"'
            response['Content-Disposition'] = file_details
            registration_qs = RegDetails.objects.filter(
                conference=event
            ).exclude(
                registration_status__in=CXL_VALUES
            ).order_by(
                *sort_orders[sort]
            )
            writer = csv.writer(response)
            writer.writerow(['Name', 'Title', 'Company'])
            for record in registration_qs:
                registrant = record.registrant
                writer.writerow([
                    registrant.first_name + ' ' + registrant.last_name,
                    registrant.title,
                    registrant.company.name
                ])
            return response

        elif report_type == 'NoName':
            sort = 'company' if sort == 'name' else sort
            file_details = destination + '; filename="delegate_list_' + \
                str(event.number) + '.csv"'
            response['Content-Disposition'] = file_details
            registration_qs = RegDetails.objects.filter(
                conference=event
            ).exclude(
                registration_status__in=CXL_VALUES
            ).order_by(
                *sort_orders[sort]
            )
            writer = csv.writer(response)
            writer.writerow(['Title', 'Company'])
            for record in registration_qs:
                registrant = record.registrant
                writer.writerow([
                    registrant.title,
                    registrant.company.name
                ])
            return response

        elif report_type == 'Registration':
            file_details = destination + '; filename="registration_list_' + \
                str(event.number) + '.csv"'
            response['Content-Disposition'] = file_details
            registration_qs = RegDetails.objects.filter(
                conference=event
            ).exclude(
                registration_status__in=NO_CONFIRMATION_VALUES
            ).order_by(*sort_orders[sort])
            writer = csv.writer(response)
            writer.writerow(['Status', 'RegDate', 'InvoiceNumber',
                             'PreTaxPrice', 'Name', 'Title', 'Company',
                             'City', 'StateProv', 'SalesCredit'])
            for record in registration_qs:
                registrant = record.registrant
                if record.invoice:
                    invoice_num = record.invoice.pk
                    pre_tax_price = record.invoice.pre_tax_price,
                    sales_credit = record.invoice.sales_credit.username
                else:
                    invoice_num = ''
                    pre_tax_price = 0
                    sales_credit = ''
                writer.writerow([
                    record.registration_status,
                    record.register_date,
                    invoice_num,
                    pre_tax_price,
                    registrant.first_name + ' ' + registrant.last_name,
                    registrant.title,
                    registrant.company.name,
                    registrant.company.city,
                    registrant.company.state_prov,
                    sales_credit,
                ])
            return response

        elif report_type == 'Phone':
            file_details = destination + '; filename="phone_list_' + \
                str(event.number) + '.csv"'
            response['Content-Disposition'] = file_details
            registration_qs = RegDetails.objects.filter(
                conference=event
            ).exclude(
                registration_status__in=NON_INVOICE_VALUES
            ).order_by(sort_orders[sort])
            writer = csv.writer(response)
            writer.writerow(['name', 'title', 'company', 'email', 'phone',
                             'city', 'stateProv', 'nameForLetters'])
            for record in registration_qs:
                registrant = record.registrant
                letter_name = ''
                if registrant.salutation:
                    letter_name += registrant.salutation + ' '
                else:
                    letter_name += registrant.first_name + ' '
                letter_name += registrant.last_name
                writer.writerow([
                    registrant.first_name + ' ' + registrant.last_name,
                    registrant.title,
                    registrant.company.name,
                    registrant.email1,
                    registrant.phone1,
                    registrant.company.city,
                    registrant.company.state_prov,
                    letter_name,
                ])
            return response

        raise Http404('Invalid Report Choice for CSV Export')

    elif doc_format == 'xlsx':
        response = HttpResponse(content_type='application/vnd.ms-excel')
        wb = Workbook()
        ws = wb.active

        if report_type == 'Delegate':
            file_details = destination + '; filename="delegate_list_' + \
                str(event.number) + '.xlsx"'
            response['Content-Disposition'] = file_details
            registration_qs = RegDetails.objects.filter(
                conference=event
            ).exclude(
                registration_status__in=CXL_VALUES
            ).order_by(
                *sort_orders[sort]
            )
            ws.append(['Name', 'Title', 'Company'])
            for record in registration_qs:
                registrant = record.registrant
                ws.append([
                    registrant.first_name + ' ' + registrant.last_name,
                    registrant.title,
                    registrant.company.name
                ])
            wb.save(response)
            return response

        elif report_type == 'NoName':
            sort = 'company' if sort == 'name' else sort
            file_details = destination + '; filename="delegate_list_' + \
                str(event.number) + '.xlsx"'
            response['Content-Disposition'] = file_details
            registration_qs = RegDetails.objects.filter(
                conference=event
            ).exclude(
                registration_status__in=CXL_VALUES
            ).order_by(
                *sort_orders[sort]
            )
            ws.append(['Title', 'Company'])
            for record in registration_qs:
                registrant = record.registrant
                ws.append([
                    registrant.title,
                    registrant.company.name
                ])
            wb.save(response)
            return response

        elif report_type == 'Registration':
            file_details = destination + '; filename="registration_list_' + \
                str(event.number) + '.xlsx"'
            response['Content-Disposition'] = file_details
            registration_qs = RegDetails.objects.filter(
                conference=event
            ).exclude(
                registration_status__in=NO_CONFIRMATION_VALUES
            ).order_by(*sort_orders[sort])
            ws.append(['Status', 'RegDate', 'InvoiceNumber', 'PreTaxPrice',
                       'Name', 'Title', 'Company', 'City', 'StateProv',
                       'SalesCredit'])
            for record in registration_qs:
                registrant = record.registrant
                if record.invoice:
                    invoice_num = record.invoice.pk
                    pre_tax_price = record.invoice.pre_tax_price,
                    sales_credit = record.invoice.sales_credit.username
                else:
                    invoice_num = ''
                    pre_tax_price = 0
                    sales_credit = ''
                ws.append([
                    record.registration_status,
                    record.register_date,
                    invoice_num,
                    pre_tax_price,
                    registrant.first_name + ' ' + registrant.last_name,
                    registrant.title,
                    registrant.company.name,
                    registrant.company.city,
                    registrant.company.state_prov,
                    sales_credit,
                ])
            wb.save(response)
            return response

        elif report_type == 'Phone':
            file_details = destination + '; filename="phone_list_' + \
                str(event.number) + '.xlsx"'
            response['Content-Disposition'] = file_details
            registration_qs = RegDetails.objects.filter(
                conference=event
            ).exclude(
                registration_status__in=NON_INVOICE_VALUES
            ).order_by(sort_orders[sort])
            ws.append(['name', 'title', 'company', 'email', 'phone', 'city',
                       'stateProv', 'nameForLetters'])
            for record in registration_qs:
                registrant = record.registrant
                letter_name = ''
                if registrant.salutation:
                    letter_name += registrant.salutation + ' '
                else:
                    letter_name += registrant.first_name + ' '
                letter_name += registrant.last_name
                ws.append([
                    registrant.first_name + ' ' + registrant.last_name,
                    registrant.title,
                    registrant.company.name,
                    registrant.email1,
                    registrant.phone1,
                    registrant.company.city,
                    registrant.company.state_prov,
                    letter_name,
                ])
            wb.save(response)
            return response

        raise Http404('Invalid Report Choice for Excel Export')

    else:
        raise Http404('Invalid document format')
