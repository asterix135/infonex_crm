from django import forms
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from registration.models import *
from crm.models import Event
from crm.constants import STATE_PROV_TUPLE, COMPANY_OPTIONS, BILLING_CURRENCY

class NewDelegateForm(forms.ModelForm):

    class Meta():
        model = Registrants
        fields = ['salutation', 'first_name', 'last_name', 'title',
                  'email1', 'email2', 'phone1', 'phone2', 'contact_option']
        labels = {
            'email1': _('Primary Email'),
            'email2': _('Secondary Email'),
            'phone1': _('Primary Phone No.'),
            'phone2': _('Secondary Phone No.'),
            'contact_option': _('Send Invoice To')
        }
        widgets = {
            'salutation': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'first_name': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'last_name': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'title': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'email1': forms.EmailInput(
                attrs={'class': 'form-control'}
            ),
            'email2': forms.EmailInput(
                attrs={'class': 'form-control'}
            ),
            'phone1': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'phone2': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'contact_option': forms.Select(
                attrs={'class': 'form-control'}
            ),
        }


class CompanySelectForm(forms.ModelForm):

    class Meta():
        model = Company
        fields = ['name', 'name_for_badges', 'address1', 'address2',
                  'city', 'state_prov', 'postal_code', 'country',
                  'gst_hst_exempt', 'qst_exempt', 'gst_hst_exemption_number',
                  'qst_exemption_number',]
        labels = {
            'name': _('Company Name'),
            'name_for_badges': _('Short Name (for badges)'),
            'address1': _('Address Line 1'),
            'address2': _('Address Line 2'),
            'gst_hst_exempt': _('GST/HST Exempt?'),
            'qst_exempt': _('QST Exempt?'),
            'gst_hst_exemption_number': _('GST/HST Exemption Number'),
            'qst_exemption_number': _('QST Exemption Number'),
        }
        widgets = {
            'name': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'name_for_badges': forms.TextInput(
                attrs={'class': 'form-control',
                       'maxlength': '10'}
            ),
            'address1': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'address2': forms.TextInput(
                attrs={'class': 'form-control'}
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
            'country': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'gst_hst_exempt': forms.CheckboxInput(
                attrs={'class': 'form-control'}
            ),
            'qst_exempt': forms.CheckboxInput(
                attrs={'class': 'form-control'}
            ),
            'gst_hst_exemption_number': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'qst_exemption_number': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
        }


class RegDetailsForm(forms.ModelForm):

    class Meta():
        model = RegDetails
        fields = ['priority_code', 'sales_credit', 'pre_tax_price', 'gst_rate',
                  'hst_rate', 'qst_rate', 'payment_date', 'payment_method',
                  'deposit_amount', 'deposit_date', 'deposit_method',
                  'fx_conversion_rate', 'register_date', 'cancellation_date',
                  'registration_status', 'invoice_notes', 'registration_notes',
                  'sponsorship_description']
        widgets = {
            'priority_code': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'sales_credit': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'pre_tax_price': forms.NumberInput(
                attrs={'class': 'form-control',
                       'step': '1'}
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
                       'step': '0.0005'}
            ),
            'payment_date': forms.DateInput(
                attrs={'class': 'form-control',
                       'placeholder': 'yyyy-mm-dd'}
            ),
            'payment_method': forms.Select(
                attrs={'class': 'form-control'}
            ),
            'deposit_amount': forms.NumberInput(
                attrs={'class': 'form-control',
                         'step': '1'}
            ),
            'deposit_date': forms.DateInput(
                attrs={'class': 'form-control',
                       'placeholder': 'yyyy-mm-dd'}
            ),
            'deposit_method': forms.Select(
                attrs={'class': 'form-control'}
            ),
            'fx_conversion_rate': forms.NumberInput(
                attrs={'class': 'form-control',
                         'step': '0.001'}
            ),
            'register_date': forms.DateInput(
                attrs={'class': 'form-control',
                       'placeholder': 'yyyy-mm-dd'}
            ),
            'cancellation_date': forms.DateInput(
                attrs={'class': 'form-control',
                       'placeholder': 'yyyy-mm-dd'}
            ),
            'registration_status': forms.Select(
                attrs={'class': 'form-control'}
            ),
            'invoice_notes': forms.Textarea(
                attrs={'class': 'form-control',
                       'rows': '4'}
            ),
            'registration_notes': forms.Textarea(
                attrs={'class': 'form-control',
                       'rows': '4'}
            ),
            'sponsorship_description': forms.Textarea(
                attrs={'class': 'form-control',
                       'rows': '4'}
            ),
        }


class AssistantForm(forms.ModelForm):

    class Meta():
        model = Assistant
        fields = ['salutation', 'first_name', 'last_name', 'title',
                  'email', 'phone', 'address_personal']
        widgets = {
            'salutation': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'first_name': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'last_name': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'title': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'email': forms.EmailInput(
                attrs={'class': 'form-control'}
            ),
            'phone': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'address_personal': forms.Textarea(
                attrs={'class': 'form-control',
                       'rows': '4'}
            )
        }


class OptionsForm(forms.Form):
    conference_options = forms.MultipleChoiceField(
        label='Select Registration Options',
        widget=forms.CheckboxSelectMultiple(
            attrs={'class': 'form-control'}
        )
    )

    def __init__(self, event, *args, **kwargs):
        super(OptionsForm, self).__init__(*args, **kwargs)
        self.fields['conference_options'] = forms.MultipleChoiceField(
            choices=[(option.id, str(option)) for
                     option in EventOptions.objects.filter(event=event)],
            widget=forms.CheckboxSelectMultiple(
                attrs={'class': 'form-control'}
            )
        )

# class OptionsForm(forms.ModelForm)
