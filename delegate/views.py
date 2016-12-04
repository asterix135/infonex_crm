from django.shortcuts import render
from django.db.models import Q

from .forms import *
from crm.models import Person
from registration.models import *
from registration.forms import ConferenceSelectForm


def index(request):
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
                crm_match_list = Person.objects.filter(
                    pk=registrant.crm_person.id
                )
            else:
                crm_match_list = Person.objects.filter(
                    Q(name__icontains=registrant.first_name) &
                    Q(name__icontains=registrant.last_name),
                    Q(company__icontains=registrant.company)
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
        'crm_match_list': crm_match_list,
    }
    return render(request, 'delegate/index.html', context)


def update_crm_match_list(request):
    crm_match_list = None
    if requst.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        company = request.POST['company']
        crm_match_list = Person.objects.filter(
            Q(name__icontains=first_name) &
            Q(name__icontains=last_name),
            Q(company__icontains-company)
        ).order_by('company', 'name')[:100]
    context = {
        'crm_match_list': crm_match_list,
    }
    return render(request, 'delegate/addins/crm_sidebar.html', context)
