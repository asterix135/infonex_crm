import datetime

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.utils import timezone

from crm.models import Contact
from . import mycharts


@login_required
def index(request):
    user = request.user
    reg_permission_ok = (user.groups.filter(name='db_admin').exists() or
                         user.groups.filter(name='registration').exists() or
                         user.groups.filter(name='management').exists() or
                         user.is_superuser)
    day_counts = {'Monday': 0,
                  'Tuesday': 0,
                  'Wednesday': 0,
                  'Thursday': 0,
                  'Friday': 0,
                  'Today': 0}
    today_contacts = Contact.objects.filter(
        # author=user,
        date_of_contact__date=datetime.datetime.today().date()
    ).count()
    day_counts['Today'] = today_contacts
    context = {'reg_permission_ok': reg_permission_ok,
               'day_counts': day_counts}
    return render(request, 'home/index.html', context)


@login_required
def recent_contact_chart(request):
    user = request.user
    today_contacts = Contact.objects.filter(
        author=user,
        date_of_contact__date=datetime.datetime.today().date()
    )
    for i in range (7):
        if timezone.now():
            pass
