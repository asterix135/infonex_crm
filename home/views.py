import datetime

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.utils import timezone

from crm.models import Contact
from . import charts


@login_required
def index(request):
    user = request.user
    reg_permission_ok = (user.groups.filter(name='db_admin').exists() or
                         user.groups.filter(name='registration').exists() or
                         user.groups.filter(name='management').exists() or
                         user.is_superuser)
    today_contacts = Contact.objects.filter(
        # author=user,
        date_of_contact__date=datetime.datetime.today().date()
    ).count()
    context = {'reg_permission_ok': reg_permission_ok,
               'today_contacts': today_contacts}
    return render(request, 'home/index.html', context)


@login_required
def recent_contact_chart(request):
    user = request.user
    contact_counts = []
    today_contacts = Contact.objects.filter(
        author=user,
        date_of_contact__date=datetime.datetime.today().date()
    )
    for i in range (0, 8):
        if timezone.now().isoweekday() - i not in [0, -1]:
            day_count = Contact.objects.filter(
                author=user,
                date_of_contact__date=(
                    timezone.now()-datetime.timedelta(days=i)
                ).date()
            ).count()
            contact_counts.append(day_count)
    print(len(contact_counts))
    print(contact_counts)
    if timezone.now().isoweekday() == 2:
        labels = ['Today', 'Monday', 'Friday', 'Thursday',
                  'Wednesday', 'Tuesday']
    elif timezone.now().isoweekday() == 3:
        labels = ['Today', 'Tuesday', 'Monday', 'Friday',
                  'Thursday', 'Wednesday']
    elif timezone.now().isoweekday() == 4:
        labels = ['Today', 'Wednesday', 'Tuesday', 'Monday',
                  'Friday', 'Thursday']
    elif timezone.now().isoweekday() == 5:
        labels = ['Today', 'Thursday', 'Wednesday', 'Tuesday',
                  'Monday', 'Friday']
    else:
        labels = ['Today', 'Friday', 'Thursday', 'Wednesday',
                  'Tuesday', 'Monday']
    contact_chart = charts.MyBarChartDrawing()
    contact_chart.chart.data = [contact_counts]
    contact_chart.title.text = 'Contacts over the Past Week'
    contact_chart.chart.categoryAxis.categoryNames = labels

    chart_object = contact_chart.asString('jpg')
    return HttpResponse(chart_object, 'image/jpg')
