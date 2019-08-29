import datetime
import re

from django import forms
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from .constants import *
from registration.models import *
from crm.models import Event
from crm.constants import *

######################
# Widget stuff
######################
def set_field_html_name(cls, new_name):
    """
    This creates wrapper around the normal widget rendering,
    allowing for a custom field name (new_name).
    """
    old_render = cls.widget.render
    def _widget_render_wrapper(name, value, attrs=None, renderer=None):
        return old_render(new_name, value, attrs, renderer)

    cls.widget.render = _widget_render_wrapper


##################
# forms
##################
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

    def clean(self):
        cleaned_data = super().clean()
        contact_option = cleaned_data.get('contact_option')
        email = cleaned_data.get('email1')
        if contact_option and contact_option in ('D', 'C'):
            if not email:
                msg = "You must indicate an email address for invoicing"
                self.add_error('contact_option',
                               'You must indicate a delegate email address ' \
                               'with this choice')
                self.add_error('email1',
                               'You must indicate an email address for invoicing')
        return cleaned_data


class CompanySelectForm(forms.ModelForm):
    crm_company = forms.CharField(max_length=255)

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
    def clean_name(self):
        if self.cleaned_data.get('name', ''):
            return self.cleaned_data.get('name', '').strip()
        return self.cleaned_data.get('name')
    def clean_name_for_badges(self):
        if self.cleaned_data.get('name_for_badges'):
            return self.cleaned_data.get('name_for_badges', '').strip()
        return self.cleaned_data.get('name_for_badges')
    def clean_city(self):
        if self.cleaned_data.get('city', ''):
            return self.cleaned_data.get('city', '').strip()
        return self.cleaned_data.get('city')
    def clean_country(self):
        if self.cleaned_data.get('country', ''):
            return self.cleaned_data.get('country', '').strip()
        return self.cleaned_data.get('country')
    def clean_postal_code(self):
        if self.cleaned_data.get('postal_code', ''):
            pc = self.cleaned_data.get('postal_code', '').strip()
            if re.match(r'\b\w\d\w\d\w\d\b', pc):
                mtch = re.match(r'\b\w\d\w\d\w\d\b', pc).group(0)
                pc = mtch[:3] + ' ' + mtch[-3:]
        else:
            pc = self.cleaned_data.get('postal_code')
        return pc


class NewCompanyForm(CompanySelectForm):
    def __init__(self, *args, **kwargs):
        super(NewCompanyForm, self).__init__(*args, **kwargs)
        # TODO: Turn this into a for loop
        set_field_html_name(self.fields['name'], 'new_company_name')
        set_field_html_name(self.fields['name_for_badges'],
                            'new_company_name_for_badges')
        set_field_html_name(self.fields['address1'], 'new_company_address1')
        set_field_html_name(self.fields['address2'], 'new_company_address2')
        set_field_html_name(self.fields['city'], 'new_company_city')
        set_field_html_name(self.fields['state_prov'], 'new_company_state_prov')
        set_field_html_name(self.fields['postal_code'],
                            'new_company_postal_code')
        set_field_html_name(self.fields['country'], 'new_company_country')
        set_field_html_name(self.fields['gst_hst_exempt'],
                            'new_company_gst_hst_exempt'),
        set_field_html_name(self.fields['qst_exempt'], 'new_company_qst_exempt')
        set_field_html_name(self.fields['gst_hst_exemption_number'],
                            'new_company_gst_hst_exemption_number')
        set_field_html_name(self.fields['qst_exemption_number'],
                            'new_company_qst_examption_number')


class RegDetailsForm(forms.ModelForm):
    register_date = forms.DateField(
        initial = datetime.date.today,
        widget = forms.DateInput(
            attrs={'class': 'form-control',
                   'placeholder': 'yyyy-mm-dd'}
        )
    )
    cancellation_date = forms.DateField(
        required = False,
        widget = forms.DateInput(
            attrs={'class': 'form-control',
                   'placeholder': 'yyyy-mm-dd'}
        )
    )
    registration_status = forms.ChoiceField(
        required=True,
        choices=REG_STATUS_OPTIONS,
        initial = '',
        widget = forms.Select(
            attrs={'class': 'form-control'}
        )
    )
    registration_notes = forms.CharField(
        required=False,
        label = 'Registration Notes (Internal Use Only)',
        widget = forms.Textarea(
            attrs={'class': 'form-control',
                   'rows': '4'}
        )
    )

    def __init__(self, *args, **kwargs):
        super(RegDetailsForm, self).__init__(*args, **kwargs)
        self.fields['sales_credit'].queryset = User.objects.filter(
            groups__name__in=('sales', 'sponsorship')
        ).exclude(is_active=False).distinct().order_by('username')
        self.fields['sales_credit'].initial = None


    class Meta():
        model = Invoice
        fields = ['sales_credit', 'pre_tax_price', 'gst_rate',
                  'hst_rate', 'qst_rate', 'payment_date', 'payment_method',
                  'fx_conversion_rate', 'invoice_notes',
                  'sponsorship_description', 'revised_flag',]
        labels = {
            'invoice_notes': _('Comments to Appear on Invoice'),
        }
        widgets = {

            'sales_credit': forms.Select(
                attrs={'class': 'form-control'}
            ),
            'pre_tax_price': forms.NumberInput(
                attrs={'class': 'cost-field form-control',
                       'step': '1'}
            ),
            'gst_rate': forms.NumberInput(
                attrs={'class': 'form-control cost-field',
                       'step': '0.01'}
            ),
            'hst_rate': forms.NumberInput(
                attrs={'class': 'form-control cost-field',
                       'step': '0.01'}
            ),
            'qst_rate': forms.NumberInput(
                attrs={'class': 'form-control cost-field',
                       'step': '0.0001'}
            ),
            'payment_date': forms.DateInput(
                attrs={'class': 'form-control',
                       'placeholder': 'yyyy-mm-dd'}
            ),
            'payment_method': forms.Select(
                attrs={'class': 'form-control'}
            ),
            'fx_conversion_rate': forms.NumberInput(
                attrs={'class': 'form-control',
                         'step': '0.001',}
            ),
            'invoice_notes': forms.Textarea(
                attrs={'class': 'form-control',
                       'rows': '4'}
            ),
            'sponsorship_description': forms.Textarea(
                attrs={'class': 'form-control',
                       'rows': '4'}
            ),
        }

    def clean(self):
        cleaned_data = super(RegDetailsForm, self).clean()
        reg_status = cleaned_data.get('registration_status')
        cxl_date = cleaned_data.get('cancellation_date')
        pre_tax_price = cleaned_data.get('pre_tax_price')
        payment_date = cleaned_data.get('payment_date')
        payment_method = cleaned_data.get('payment_method')

        if reg_status and reg_status in CXL_VALUES:
            if not cxl_date:
                self.add_error('cancellation_date',
                               'Cancellation Date Required')
        if reg_status and reg_status not in ZERO_INVOICE_OK:
            if not pre_tax_price:
                if reg_status in PAID_STATUS_VALUES:
                    if payment_method and payment_method != 'N':
                        self.add_error('pre_tax_price',
                                       'You must indicate the registration fee')
                else:
                    self.add_error('pre_tax_price',
                                   'You must indicate the registration fee')

        if reg_status and reg_status in PAID_STATUS_VALUES:
            if not payment_date:
                self.add_error('payment_date',
                               'You must indicate payment date')
            if not payment_method:
                self.add_error('payment_method',
                               'You must indicate method of payment')
        return cleaned_data


class AssistantForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(AssistantForm, self).__init__(*args, **kwargs)
        self.fields['last_name'].required = False
        # TODO: Turn this into a for loop
        set_field_html_name(self.fields['salutation'], 'assistant_salutation')
        set_field_html_name(self.fields['first_name'], 'assistant_first_name')
        set_field_html_name(self.fields['last_name'], 'assistant_last_name')
        set_field_html_name(self.fields['title'], 'assistant_title')
        set_field_html_name(self.fields['email'], 'assistant_email')
        set_field_html_name(self.fields['phone'], 'assistant_phone')
        set_field_html_name(self.fields['address_personal'], 'assistant_address')

    class Meta():
        model = Assistant
        fields = ['salutation', 'first_name', 'last_name', 'title',
                  'email', 'phone', 'address_personal']
        widgets = {
            'salutation': forms.TextInput(
                attrs={'class': 'form-control',
                       'id': 'assistant_salutation',}
            ),
            'first_name': forms.TextInput(
                attrs={'class': 'form-control assistant-field',
                       'id': 'assistant_first_name'}
            ),
            'last_name': forms.TextInput(
                attrs={'class': 'form-control assistant-field',
                       'id': 'assistant_last_name'}
            ),
            'title': forms.TextInput(
                attrs={'class': 'form-control assistant-field',
                       'id': 'assistant_title'}
            ),
            'email': forms.EmailInput(
                attrs={'class': 'form-control assistant-field',
                       'id': 'assistant_email'}
            ),
            'phone': forms.TextInput(
                attrs={'class': 'form-control assistant-field',
                       'id': 'assistant_phone'}
            ),
            'address_personal': forms.Textarea(
                attrs={'class': 'form-control',
                       'rows': '4',
                       'id': 'assistant_address'}
            )
        }

    def clean_salutation(self):
        if self.cleaned_data.get('salutation', ''):
            return self.cleaned_data.get('salutation', '').strip()
        return self.cleaned_data.get('salutation', '')
    def clean_first_name(self):
        if self.cleaned_data.get('first_name', ''):
            return self.cleaned_data.get('first_name', '').strip()
        return self.cleaned_data.get('first_name', '')
    def clean_last_name(self):
        if self.cleaned_data.get('last_name', ''):
            return self.cleaned_data.get('last_name', '').strip()
        return self.cleaned_data.get('last_name', '')
    def clean_title(self):
        if self.cleaned_data.get('title', ''):
            return self.cleaned_data.get('title', '').strip()
        return self.cleaned_data.get('title', '')
    def clean_email(self):
        if self.cleaned_data.get('email', ''):
            return self.cleaned_data.get('email', '').strip()
        return self.cleaned_data.get('email', '')
    def clean_phone(self):
        if self.cleaned_data.get('phone', ''):
            return self.cleaned_data.get('phone', '').strip()
        return self.cleaned_data.get('phone', '')


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


class EmailMessageForm(forms.Form):
    message = forms.CharField(
        strip=True,
        label='Email Message',
        widget=forms.Textarea(
            attrs={'class': 'form-control'}
        )
    )
    subject = forms.CharField(
        strip=True,
        label='Subject Line',
        widget=forms.TextInput(
            attrs={'class': 'form-control'}
        )
    )
