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
        fields = ['name']
        labels = {
            'name': _('Company Name'),
        }
        widgets = {
            'name': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
        }
