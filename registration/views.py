from django.shortcuts import render
from django.http import HttpResponse
from .forms import *
from .models import *
from crm.models import Person


def index(request):
    return render(request, 'registration/index.html')

def new_delegate_search(request):
    if request.method == 'POST':
        person_form = NewDelegateSearchForm(request.POST)
        filterargs = {
            'first_name__icontains': request.POST['first_name'],
            'last_name__icontains': request.POST['last_name'],

        }
        past_customer_list = Registrants.objects.filter(**filterargs)
        crm_filterargs = {
            'name__icontains': request.POST['first_name'],
            'name__icontains': request.POST['last_name'],
            'company__icontains': request.POST['company']
        }
        crm_list = Person.objects.filter(**crm_filterargs)
    else:
        person_form = NewDelegateSearchForm()
        past_customer_list = None
        crm_list = None
    past_customer_list = None
    context = {
        'person_form': person_form,
        'past_customer_list': past_customer_list,
        'crm_list': crm_list,
    }
    return render(request, 'registration/new_reg.html', context)
