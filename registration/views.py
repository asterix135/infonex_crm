from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return render(request, 'registration/index.html')

def new(request):
    return render(request, 'registration/new_reg.html')
