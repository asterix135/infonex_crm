from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.http import HttpResponse

# def index(request):
#     return HttpResponse('This is the home page for all web apps')

def index(request):
    return render(request, 'home/index.html')
