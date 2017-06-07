from django import forms
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from .models import *
from .widgets import MonthYearWidget
from crm.models import Event
from crm.constants import COMPANY_OPTIONS, BILLING_CURRENCY
from .constants import *


#######################
# FORMS
#######################
class NewDelegateSearchForm(forms.Form):
    first_name = forms.CharField(label='First Name',
                                 max_length=100,
                                 required=False,
                                 widget=forms.TextInput(
                                     attrs={'class': 'form-control'}
                                 ))
    last_name = forms.CharField(label='Last Name',
                                max_length=100,
                                required=False,
                                widget=forms.TextInput(
                                    attrs={'class': 'form-control'}
                                ))
    company = forms.CharField(label='Company',
                              max_length=100,
                              required=False,
                              widget=forms.TextInput(
                                  attrs={'class': 'form-control'}
                              ))
    postal_code = forms.CharField(label='postal_code',
                                  max_length=100,
                                  required=False,
                                  widget=forms.TextInput(
                                      attrs={'class': 'form-control'}
                                  ))
    event = forms.ModelChoiceField(
        label='Select Conference',
        required=False,
        initial='',
        queryset=Event.objects.none(),
        widget=forms.Select(
            attrs={'class': 'form-control'}
        )
    )

    def __init__(self, *args, **kwargs):
        super(NewDelegateSearchForm, self).__init__(*args, **kwargs)
        self.fields['event'].queryset=Event.objects.filter(
                date_begins__gte=timezone.now()-datetime.timedelta(weeks=4)
        ).order_by('-number')


class ConferenceEditForm(forms.ModelForm):
    gst_rate = forms.FloatField(required=False, initial=0.05)
    hst_rate = forms.FloatField(required=False, initial=0.13)
    qst_rate = forms.FloatField(required=False, initial=0.09975)

    def __init__(self, *args, **kwargs):
        super(ConferenceEditForm, self).__init__(*args, **kwargs)
        self.fields['developer'].queryset = User.objects.filter(
            groups__name='conference_developer'
        ).order_by('username')
        self.fields['registrar'].queryset = User.objects.filter(
            groups__name='registration'
        ).order_by('username')

    class Meta():
        model = Event
        fields = ['number', 'title', 'city', 'date_begins', 'state_prov',
                  'hotel', 'registrar', 'developer', 'company_brand',
                  'gst_charged', 'hst_charged', 'qst_charged',
                  'gst_rate', 'hst_rate', 'qst_rate', 'billing_currency',
                  'event_web_site', 'default_dept', 'default_cat1',
                  'default_cat2']
        labels = {
            'number': _('Event Number'),
            'title': _('Event Title'),
            'date_begins': _('Event Start Date'),
            'default_dept': _('Default Department for CRM'),
            'default_cat1': _('Default CRM Category(1)'),
            'default_cat2': _('Default CRM Category(2)'),
        }
        widgets = {
            'number': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'title': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'city': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'date_begins': forms.DateInput(
                attrs={'class': 'form-control',
                       'placeholder': 'yyyy-mm-dd'}
            ),
            'state_prov': forms.Select(
                attrs={'class': 'form-control'}
            ),
            'hotel': forms.Select(
                attrs={'class': 'form-control'}
            ),
            'registrar': forms.Select(
                attrs={'class': 'form-control'}
            ),
            'developer': forms.Select(
                attrs={'class': 'form-control'}
            ),
            'company_brand': forms.Select(
                attrs={'class': 'form-control'}
            ),
            'gst_charged': forms.CheckboxInput(
                attrs={'class': 'form-control event-checkbox'}
            ),
            'hst_charged': forms.CheckboxInput(
                attrs={'class': 'form-control event-checkbox'}
            ),
            'qst_charged': forms.CheckboxInput(
                attrs={'class': 'form-control event-checkbox',}
            ),
            'gst_rate': forms.NumberInput(
                attrs={'class': 'form-control',
                       'step': '0.01'}
            ),
            'hst_rate': forms.NumberInput(
                attrs={'class': 'form-control',
                       'step': '0.01'}
            ),
            'qst_rate': forms.NumberInput(
                attrs={'class': 'form-control',
                       'step': '0.001'}
            ),
            'billing_currency': forms.Select(
                attrs={'class': 'form-control'}
            ),
            'event_web_site': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'default_dept': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'default_cat1': forms.Select(
                attrs={'class': 'form-control'}
            ),
            'default_cat2': forms.Select(
                attrs={'class': 'form-control'}
            ),
        }

    def clean(self):
        cleaned_data = super(ConferenceEditForm, self).clean()
        gst_charged = cleaned_data.get('gst_charged')
        gst_rate = cleaned_data.get('gst_rate')
        hst_charged = cleaned_data.get('hst_charged')
        hst_rate = cleaned_data.get('hst_rate')
        qst_charged = cleaned_data.get('qst_charged')
        qst_rate = cleaned_data.get('qst_rate')

        if gst_charged:
            if not gst_rate:
                self.add_error('gst_rate',
                               'You forgot to enter the GST Rate')
        elif not gst_rate:
            self.cleaned_data['gst_rate'] = 0
        if hst_charged:
            if not hst_rate:
                self.add_error('hst_rate',
                               'You forgot to enter the HST Rate')
        elif not hst_rate:
            self.cleaned_data['hst_rate'] = 0
        if qst_charged:
            if not qst_rate:
                self.add_error('qst_rate',
                               'You forgot to enter the QST Rate')
        elif not qst_rate:
            self.cleaned_data['qst_rate'] = 0
        if gst_charged and hst_charged:
            self.add_error('gst_charged',
                           'You cannot charge both GST and HST')
            self.add_error('hst_charged',
                           'You cannot charge both GST and HST')


class ConferenceOptionForm(forms.ModelForm):

    class Meta:
        model = EventOptions
        fields = ('name', 'startdate', 'enddate', 'primary')
        widgets = {
            'name': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'startdate': forms.DateInput(
                attrs={'class': 'form-control',
                       'placeholder': 'yyyy-mm-dd'}
            ),
            'enddate': forms.DateInput(
                attrs={'class': 'form-control',
                       'placeholder': 'yyyy-mm-dd'}
            ),
            'primary': forms.CheckboxInput(
                attrs={'class': 'form-control'}
            )
        }


class VenueForm(forms.ModelForm):

    class Meta:
        model = Venue
        fields = ['name', 'address', 'city', 'state_prov', 'postal_code',
                  'phone', 'hotel_url']
        widgets = {
            'name': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'address': forms.Textarea(
                attrs={'class': 'form-control',
                       'rows': '2',}
            ),
            'city': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'state_prov': forms.Select(
                attrs={'class': 'form-control'}
            ),
            'postal_code': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'phone': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'hotel_url': forms.URLInput(
                attrs={'class': 'form-control'}
            )
        }
        labels = {
            'name': _('Name of Venue'),
        }

    def __init__(self, *args, **kwargs):
        super(VenueForm, self).__init__(*args, **kwargs)
        self.fields['state_prov'] = forms.ChoiceField(
            choices=STATE_PROV_TUPLE,
            widget=forms.Select(
                attrs={'class': 'form-control'}
            ),
            initial='ON',
        )


class ConferenceSelectForm(forms.Form):
    event = forms.ModelChoiceField(
        label='Select Conference',
        required=False,
        initial='',
        queryset=Event.objects.filter(
            date_begins__gte=timezone.now()-datetime.timedelta(weeks=4)
        ).order_by('-number'),
        widget=forms.Select(
            attrs={'class': 'form-control col-sm-4'}
        )
    )


class AdminReportOptionsForm(forms.Form):
    report = forms.ChoiceField(
        label='What kind of report do you want?',
        required=True,
        initial=ADMIN_REPORTS[0][0],
        choices=ADMIN_REPORTS,
        widget=forms.RadioSelect()
    )
    sort = forms.ChoiceField(
        label='How should the records be sorted?',
        required=True,
        initial='name',
        choices=(('name', 'by Name (Last name then First name)'),
                 ('title', 'by Title'),
                 ('company', 'by Company')),
        widget=forms.RadioSelect()
    )
    destination = forms.ChoiceField(
        label='How do you want to get the report?',
        required=True,
        initial='attachment',
        choices=(('attachment', 'Download'),
                 ('inline', 'New Window')),
        widget=forms.RadioSelect()
    )
    report_format = forms.ChoiceField(
        label="What format should the report be in?",
        required=True,
        initial='pdf',
        choices=(('pdf', 'PDF'),
                 ('csv', 'CSV (comma-delimted text)'),
                 ('xlsx', 'Excel (.xlsx)')),
        widget=forms.RadioSelect()
    )


class SalesReportOptionsForm(forms.Form):
    report_date = forms.DateField(
        label='Select the Report Month and Year',
        required = True,
        widget=MonthYearWidget(
            attrs={'class': 'form-control col-sm-4'}
        )
    )


class MassMailOptionsForm(forms.Form):
    mass_mail_message = forms.ChoiceField(
        label='What email do you want to send?',
        required=True,
        # initial=MASS_MAIL_CHOICES[0][0],
        choices=MASS_MAIL_CHOICES,
        widget=forms.RadioSelect()
    )


class MailMergeDetailsForm(forms.Form):
    venue_details = forms.CharField(
        label="Confirm Venue Details",
        required=True,
        widget=forms.Textarea(
            attrs={'class': 'form-control',
                   'rows': '5'}
        )
    )
    event_registrar = forms.CharField(
        label='Event Registrar (Who the email is from)',
        required=True,
        widget=forms.Textarea(
            attrs={'class': 'form-control',
                   'rows': '3'}
        )
    )
    room_rate = forms.CharField(
        label='Bedroom rate',
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control',
                   'placeholder': 'e.g.: $249 per night'}
        )
    )
    room_rate_code = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control'}
        )
    )
    room_booking_phone = forms.CharField(
        required=False,
        label='Bedroom reservation number',
        widget=forms.TextInput(
            attrs={'class': 'form-control'}
        )
    )
    conference_name = forms.CharField(
        label='Conference Name',
        required=True,
        widget=forms.TextInput(
            attrs={'class': 'form-control'}
        )
    )
    conference_location = forms.CharField(
        label='Conference Location',
        required = True,
        widget=forms.TextInput(
            attrs={'class': 'form-control'}
        )
    )
    start_date = forms.CharField(
        label='Start Date',
        required=True,
        widget=forms.TextInput(
            attrs={'class': 'form-control'}
        )
    )
    download_link = forms.URLField(
        label='Conference Download URL',
        required=False,
        widget=forms.URLInput(
            attrs={'class': 'form-control'}
        )
    )
    registration_start = forms.CharField(
        label='Registration/Breakfast Start',
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control',
                   'placeholder': 'e.g.: 8:00 a.m.'}
        )
    )
    opening_remarks_time = forms.CharField(
        label='Time of Opening Remarks',
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control',
                   'placeholder': 'e.g.: 9:00 am'}
        )
    )
