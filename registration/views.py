from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Q
from django.template import RequestContext
from .forms import *
from .models import *
from crm.models import Person


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
        # do something
        person = Registrants.objects.get(pk=person_id)
        person_regs = person.regdetails_set.all()
    return render(request, 'registration/addins/reg_history.html',
        {'person_regs': person_regs})

def add_new_delegate(request):
    return render(request, 'registration/add_new_delegate.html')


def add_conference(request):
    venue_form = VenueForm()
    context = {
        'venue_form': venue_form,
    }
    return render(request, 'registration/conference.html', context)
