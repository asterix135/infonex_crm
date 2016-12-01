from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Q
from django.template import RequestContext
from django.utils import timezone
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


def filter_venue(request):
    venue_form = VenueForm()
    try:
        city_partial = request.GET['city_partial']
    except MultiValueDictKeyError:
        city_partial = None
    venue_list = Venue.objects.filter(
        city__icontains=city_partial).order_by('city', 'name')
    context = {
        'venue_form': venue_form,
        'venue_list': venue_list,
    }
    return render(request, 'registration/addins/venue_sidebar.html', context)


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


def create_temp_conf_number():
    """ helper function for add_event_option """
    base_number = "TEMP"
    counter = 0
    while True:
        event_number = base_number + str(counter)
        if len(Event.objects.filter(number=event_number)) == 0:
            return event_number
        counter += 1


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
        # form_data = {
        #     'primary': request.POST['primary'],
        #     'name': request.POST['name'],
        #     'startdate': request.POST['startdate'],
        #     'enddate': request.POST['enddate'],
        # }
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
