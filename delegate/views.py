from django.shortcuts import render

from .forms import *
from registration.forms import ConferenceSelectForm


def index(request):
    new_delegate_form = NewDelegateForm()
    company_select_form = CompanySelectForm()
    conference_select_form = ConferenceSelectForm()
    context = {
        'new_delegate_form': new_delegate_form,
        'company_select_form': company_select_form,
        'conference_select_form': conference_select_form,
    }
    return render(request, 'delegate/index.html', context)
