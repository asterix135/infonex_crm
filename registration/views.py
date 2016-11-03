from django.shortcuts import render
from django.http import HttpResponse
from .forms import *


def index(request):
    return render(request, 'registration/index.html')

def new(request):
    person_form = NewDelegateSearchForm()
    context = {
        'person_form': person_form,
    }
    return render(request, 'registration/new_reg.html', context)
