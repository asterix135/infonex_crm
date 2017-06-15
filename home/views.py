import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.utils import timezone

from crm.models import Contact
from registration.models import RegDetails, Invoice
from . import charts


#############################
# primary page views
#############################
class Index(TemplateView):
    template_name = 'home/index.html'

    def _get_sales_data(self):
        current_month = datetime.datetime.today().month
        current_year = datetime.datetime.today().year
        user = self.request.user
        if (user.groups.filter(name='sales').exists() or
            user.groups.filter(name='sponsorship').exists()):
            user_bookings = Invoice.objects.filter(sales_credit=user)
        elif user.groups.filter(name='conference_developer').exists():
            user_bookings = Invoice.objects.filter(
                reg_details__conference__developer=user
            )
        elif (user.groups.filter(name='management').exists or user.is_superuser):
            user_bookings = Invoice.objects.all()
        else:
            user_bookings = Invoice.objects.none()
        month_bookings = user_bookings.filter(
            reg_details__register_date__month=current_month,
            reg_details__register_date__year=current_year
        ).aggregate(Sum('pre_tax_price'))['pre_tax_price__sum']
        monthly_payments = user_bookings.filter(
            payment_date__month=current_month,
            payment_date__year=current_year
        ).aggregate(Sum('pre_tax_price'))['pre_tax_price__sum']
        if not month_bookings:
            month_bookings = 0
        if not monthly_payments:
            monthly_payments = 0
        return month_bookings, monthly_payments

    def _get_month_regs(self):
        month = self.request.GET.get('month',
                                     datetime.datetime.today().month)
        year = self.request.GET.get('year',
                                    datetime.datetime.today().year)
        user = self.request.user
        month_regs = RegDetails.objects.filter(
            register_date__year=year,
            register_date__month=month,
            invoice__sales_credit=user,
        ).order_by('register_date')
        return month_regs

    def _get_month_payments(self):
        month = self.request.GET.get('month',
                                     datetime.datetime.today().month)
        year = self.request.GET.get('year',
                                    datetime.datetime.today().year)
        user = self.request.user
        month_payments = RegDetails.objects.filter(
            invoice__payment_date__year=year,
            invoice__payment_date__month=month,
            invoice__sales_credit=user,
        ).order_by('register_date')
        return month_payments

    def get_context_data(self, **kwargs):
        context = super(Index, self).get_context_data(**kwargs)
        user = self.request.user
        context['reg_permission_ok'] = (
            user.groups.filter(name='db_admin').exists() or
            user.groups.filter(name='registration').exists() or
            user.groups.filter(name='management').exists() or
            user.is_superuser
        )
        context['today_contacts'] = \
            today_contacts = Contact.objects.filter(
                author=user,
                date_of_contact__date=datetime.datetime.today().date()
            ).count()
        month_sales, month_payments = self._get_sales_data()
        context['month_sales'] = month_sales
        context['month_payments'] = month_payments
        if user.groups.filter(name='sales').exists() or \
            user.groups.filter(name='sponsorship').exists() or \
            user.is_superuser:
            context['month_reg_list'] = self._get_month_regs()
            context['month_payment_list'] = self._get_month_payments()
        return context


###########################
# Page elements
###########################
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

    chart_object = contact_chart.asString('png')
    return HttpResponse(chart_object, 'image/png')
