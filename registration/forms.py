from django import forms
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from .models import *
from crm.models import Event
from crm.constants import STATE_PROV_TUPLE, COMPANY_OPTIONS, BILLING_CURRENCY


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
                  'event_web_site']
        labels = {
            'number': _('Event Number'),
            'title': _('Event Title'),
            'date_begins': _('Event Start Date'),
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
        }

        def clean(self):
            super(ContactForm, self).clean()
            # https://docs.djangoproject.com/en/1.10/ref/forms/validation/#cleaning-and-validating-fields-that-depend-on-each-other
            # deal with GST/HST/QST matching fields here


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
        label='Select Report Type',
        required=True,
        initial='',
        choices=ADMIN_REPORTS,
        widget=forms.RadioSelect(
            attrs={'class': 'form-control'}
        )
    )
