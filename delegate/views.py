from django.shortcuts import render
from django.db.models import Q

from .forms import *
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
    conference = None
    conference_options = None
    registrant = None
    company = None
    assistant = None
    crm_match = None
    crm_match_list = None
    if request.method == 'POST':
        conf_id = request.POST['conf_id']
        conference = Event.objects.get(pk=conf_id)
        conference_options = conference.eventoptions_set.all()
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
        'new_delegate_form': new_delegate_form,
        'company_select_form': company_select_form,
        'assistant_form': assistant_form,
        'conference_select_form': conference_select_form,
        'reg_details_form': reg_details_form,
        'conference': conference,
        'conference_options': conference_options,
        'registrant': registrant,
        'company': company,
        'assistant': assistant,
        'crm_match': crm_match,
        'crm_match_list': crm_match_list,
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
