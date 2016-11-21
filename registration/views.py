from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Q
from django.template import RequestContext
from django.utils.datastructures import MultiValueDictKeyError

from .forms import *
from .models import *
from crm.models import Person, Event


def index(request):
    return render(request, 'registration/index.html')


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
    else:
        past_customer_list = None
        crm_list = None
        search_entered = None
    context = {
        'past_customer_list': past_customer_list,
        'crm_list': crm_list,
        'search_entered': search_entered,
    }
    return render(request, 'registration/addins/match_del_list.html', context)


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


def add_new_delegate(request):
    return render(request, 'registration/add_new_delegate.html')


def add_edit_conference(request):
    """ Renders conference page """
    edit_action = 'blank'
    edit_venue = None
    conference_edit_form = None
    if request.method == 'GET':
        edit_action = request.GET.get('action', 'blank')
        if edit_action not in ('blank', 'new', 'edit'):
            edit_action = 'blank'
        if edit_action == 'edit':
            try:
                edit_event = Event.objects.get(pk=request.GET['id'])
                # TODO: Fix this (fix the form?)
                conference_edit_form = ConferenceEditForm()
            except (Event.DoesNotExist, MultiValueDictKeyError):
                edit_action = 'blank'
        elif edit_action == 'new':
            conference_edit_form = ConferenceEditForm()

    venue_list = Venue.objects.all().order_by('city', 'name')
    venue_form = VenueForm()
    conference_select_form = ConferenceSelectForm()
    context = {
        'venue_form': venue_form,
        'venue_list': venue_list,
        'conference_select_form': conference_select_form,
    }
    return render(request, 'registration/conference.html', context)


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


def add_venue(request):
    """ AJAX Function to add new venue and refresh venue sidebar """
    errors = False
    # TODO: Update this when filter function implemented
    venue_list = Venue.objects.all().order_by('city', 'name')
    if request.method == 'POST':
        venue_form = VenueForm(request.POST)
        if venue_form.is_valid():
            venue_form.save()
            venue_form = VenueForm()
    else:
        venue_form = VenueForm()
        errors = True
    context = {
        'venue-form': venue_form,
        'venue_list': venue_list,
        'errors': errors,
    }
    return render(request, 'registration/addins/venue_sidebar.html', context)
