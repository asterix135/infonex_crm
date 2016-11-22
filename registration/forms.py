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


class ConferenceEditFormNEW(forms.ModelForm):

    class Meta():
        model = Event
        fields = ['number', 'title', 'city', 'date_begins', 'state_prov',
                  'hotel', 'registrar', 'developer', 'company_brand',
                  'gst_charged', 'hst_charged', 'qst_charged',
                  'gst_rate', 'hst_rate', 'qst_rate', 'billing_currency']
        labels = {
            'number': _('Event Number'),
            'title': _('Event Title'),
            'date_begins': _('First Date of Event'),
        }
        widgets = {
            
        }


class ConferenceEditForm(forms.Form):
    event_number = forms.CharField(
        label='Event Number',
        max_length=10,
        required=True,
        widget=forms.TextInput(
            attrs={'class': 'form-control'}
        )
    )
    conference_title = forms.CharField(
        label='Conference Title',
        max_length=100,
        required=True,
        widget=forms.TextInput(
            attrs={'class': 'form-control'}
        )
    )
    start_date = forms.DateField(
        label='First Day of Event',
        required=True,
        widget=forms.DateInput(
            attrs={'class': 'form-control'}
        )
    )
    city = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(
            attrs={'class': 'form-control'}
        )
    )
    state_prov = forms.ChoiceField(
        label='State/Province',
        required=True,
        choices=STATE_PROV_TUPLE,
        initial='ON',
        widget=forms.Select(
            attrs={'class': 'form-control'}
        )
    )
    hotel = forms.ModelChoiceField(
        label='hotel',
        required=False,
        queryset=Venue.objects.all().order_by('name'),
        initial='',
        widget=forms.Select(
            attrs={'class': 'form-control'}
        )
    )
    registrar = forms.ModelChoiceField(
        required=True,
        queryset=User.objects.filter(is_active=True).order_by('username'),
        initial='',
        widget=forms.Select(
            attrs={'class': 'form-control'}
        )
    )
    developer = forms.ModelChoiceField(
        required=True,
        queryset=User.objects.filter(is_active=True).order_by('username'),
        initial='',
        widget=forms.Select(
            attrs={'class': 'form-control'}
        )
    )
    company_brand = forms.ChoiceField(
        required=True,
        label='Corporate Brand',
        choices=COMPANY_OPTIONS,
        initial='IC',
        widget=forms.Select(
            attrs={'class': 'form-control'}
        )
    )
    gst_charged = forms.BooleanField(
        label='Charge GST?',
        initial=False,
        required=False,
        widget=forms.CheckboxInput(
            attrs={'class': 'form-control'}
        )
    )
    hst_charged = forms.BooleanField(
        label='Charge HST?',
        initial=True,
        required=False,
        widget=forms.CheckboxInput(
            attrs={'class': 'form-control'}
        )
    )
    qst_charged = forms.BooleanField(
        label='Charge QST?',
        initial=False,
        required=False,
        widget=forms.CheckboxInput(
            attrs={'class': 'form-control'}
        )
    )
    gst_rate = forms.DecimalField(
        required=False,
        label='GST Rate',
        initial=0.05,
        widget=forms.NumberInput(
            attrs={'class': 'form-control'}
        )
    )
    hst_rate = forms.DecimalField(
        required=False,
        label='HST Rate',
        initial=0.13,
        widget=forms.NumberInput(
            attrs={'class': 'form-control'}
        )
    )
    qst_rate = forms.DecimalField(
        required=False,
        label='QST Rate',
        initial=0.09975,
        widget=forms.NumberInput(
            attrs={'class': 'form-control'}
        )
    )
    billing_currency = forms.ChoiceField(
        required=True,
        label='Billing Currency',
        choices=BILLING_CURRENCY,
        initial='CAD',
        widget=forms.Select(
            attrs={'class': 'form-control'}
        )
    )

    def clean(self):
        # https://docs.djangoproject.com/en/1.10/ref/forms/validation/#cleaning-and-validating-fields-that-depend-on-each-other
        # deal with GST/HST/QST matching fields here
        pass


class ConferenceOptionForm(forms.ModelForm):

    class Meta:
        model = EventOptions
        fields = ('name', 'startdate', 'enddate',)
        widgets = {
            'name': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'startdate': forms.DateInput(
                attrs={'class': 'form-control'}
            ),
            'enddate': forms.DateInput(
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
