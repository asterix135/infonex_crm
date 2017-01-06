from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.http import HttpResponse

# def index(request):
#     return HttpResponse('This is the home page for all web apps')

@login_required
def index(request):
    user = request.user
    reg_permission_ok = (user.groups.filter(name='db_admin').exists() or
                         user.groups.filter(name='registration').exists() or
                         user.groups.filter(name='management').exists() or
                         user.is_superuser)
    context = {'reg_permission_ok': reg_permission_ok}
    return render(request, 'home/index.html', context)
