from django import forms
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from .models import *
from .constants import STATE_PROV_TUPLE, FLAG_CHOICES
from delegate.forms import set_field_html_name


#################
# Renderers
#################
class HorizontalRadioRenderer(forms.RadioSelect.renderer):
    def render(self):
        return mark_safe(u'\n'.join([u'%s\n' % w for w in self]))


#################
# Forms
#################
class MasterTerritoryForm(forms.ModelForm):

    class Meta:
        model = MasterListSelections
        fields = ('geo', 'main_category', 'main_category2', 'company',
                  'industry', 'include_exclude', 'dept')
        labels = {
            'dept': _('Department'),
            'geo': _('Geographic Group'),
            'main_category': _('Main Category (F1)'),
            'main_category2': _('Secondary Category'),
        }
        widgets = {
            'dept': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'geo': forms.Select(
                attrs={'class': 'form-control'}
            ),
            'main_category': forms.Select(
                attrs={'class': 'form-control'}
            ),
            'main_category2': forms.Select(
                attrs={'class': 'form-control'}
            ),
            'company': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'industry': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'include_exclude': forms.Select(
                attrs={'class': 'form-control'}
            )
        }


class NewPersonForm(forms.ModelForm):

    class Meta:
        model = Person
        fields = ('name', 'title', 'company', 'url', 'linkedin', 'phone',
                  'phone_main', 'email', 'do_not_call', 'do_not_email',
                  'city', 'dept', 'industry', 'geo', 'main_category',
                  'main_category2', 'division1', 'division2',
                  'phone_alternate', 'email_alternate')
        labels = {
            'url': _('Website'),
            'linkedin': _('LinkedIn Profile'),
            'industry': _('Industry Description'),
            'dept': _('Department'),
            'geo': _('Geographic Group'),
            'main_category': _('Main Category (F1)'),
            'main_category2': _('Secondary Category'),
            'division1': _('Main Sales Division'),
            'division2': _('Secondary Sales Division'),
            'phone_alternate': _('Alternate Phone Number'),
            'email_alternate': _('Alternate Email'),
        }
        widgets = {
            'name': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'title': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'company': forms.TextInput(
                attrs={'class': 'form-control',
                       'data-provide': 'typeahead',
                       'autocomplete': 'off',}
            ),
            'url': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'linkedin': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'phone': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'phone_alternate': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'phone_main': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'email': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'email_alternate': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'do_not_call': forms.CheckboxInput(
                attrs={'class': 'form-control'}
            ),
            'do_not_email': forms.CheckboxInput(
                attrs={'class': 'form-control'}
            ),
            'city': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'dept': forms.TextInput(
                attrs={'class': 'form-control',
                       'placeholder': "OK to leave blank"}
            ),
            'industry': forms.Textarea(
                attrs={'class': 'form-control',
                       'rows': '3'}
            ),
            'geo': forms.Select(
                attrs={'class': 'form-control'}
            ),
            'main_category': forms.Select(
                attrs={'class': 'form-control'}
            ),
            'main_category2': forms.Select(
                attrs={'class': 'form-control'}
            ),
            'division1': forms.Select(
                attrs={'class': 'form-control'}
            ),
            'division2': forms.Select(
                attrs={'class': 'form-control'}
            ),
        }


class NewContactForm(forms.ModelForm):

    class Meta:
        model = Contact
        fields = ('event', 'method', 'notes')
        widgets = {
            'event': forms.Select(
                attrs={'class': 'form-control'}
            ),
            'method': forms.Select(
                attrs={'class': 'form-control'}
            ),
            'notes': forms.Textarea(
                attrs={'class': 'form-control',
                       'rows': '3'}
            ),
        }

    def __init__(self, *args, **kwargs):
        super(NewContactForm, self).__init__(*args, **kwargs)
        self.fields['event'].queryset=Event.objects.filter(
                date_begins__gte=timezone.now()-datetime.timedelta(weeks=4)
        ).order_by('-number')


class PersonDetailsForm(forms.ModelForm):

    class Meta:
        model = Person
        fields = ('name', 'title', 'company', 'url', 'phone', 'phone_main',
                  'do_not_call', 'email', 'do_not_email', 'industry',
                  'city', 'linkedin', 'phone_alternate', 'email_alternate',)
        labels = {
            'url': _('Website'),
            'linkedin': _('LinkedIn Profile'),
            'industry': _('Industry Description'),
            'phone_alternate': _('Alternate Phone Number'),
            'email_alternate': _('Alternate Email'),
        }
        widgets = {
            'name': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'title': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'company': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'url': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'city': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'phone': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'phone_alternate': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'phone_main': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'email': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'email_alternate': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'industry': forms.Textarea(
                attrs={'class': 'form-control',
                       'rows': '3'}
            ),
            'linkedin': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
        }


class PersonCategoryUpdateForm(forms.ModelForm):
    """
    Used to update category info for a person in the crm database
    """

    class Meta:
        model = Person
        fields = ('dept', 'geo', 'main_category', 'main_category2',
                  'division1', 'division2',)
        labels = {
            'dept': _('Department'),
            'geo': _('Geographic Group'),
            'main_category': _('Main Category (F1)'),
            'main_category2': _('Secondary Category'),
            'division1': _('Main Sales Division'),
            'division2': _('Secondary Sales Division'),
        }
        widgets = {
            'dept': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'geo': forms.Select(
                attrs={'class': 'form-control'}
            ),
            'main_category': forms.Select(
                attrs={'class': 'form-control'}
            ),
            'main_category2': forms.Select(
                attrs={'class': 'form-control'}
            ),
            'division1': forms.Select(
                attrs={'class': 'form-control'}
            ),
            'division2': forms.Select(
                attrs={'class': 'form-control'}
            ),
        }


class PersonTerritorySelectMethodForm(forms.ModelForm):
    """
    Used to select if staff member territory is a filter of master or
    if it is a selection from entire database
    """

    class Meta:
        model = EventAssignment
        fields = ('filter_master_selects',)

    def __init__(self, *args, **kwargs):
        super(PersonTerritorySelectMethodForm, self).__init__(*args, **kwargs)
        self.fields['filter_master_selects'] = forms.ChoiceField(
            choices=PERSON_MASTER_RELATION_CHOICES,
            widget=forms.RadioSelect(
                renderer=HorizontalRadioRenderer,
                attrs={'class': 'radio-inline'}
            ),
        )
        self.fields['filter_master_selects'].label = \
            'Filter the master selects or start from scratch?'


class PersonalTerritorySelects(forms.ModelForm):
    """
    :param filter_master_bool: (default=True) whether to filter master (True)
        or create from scratch (False)
    :type filter_master_bool: boolean
    """

    class Meta:
        model = PersonalListSelections
        fields = ('geo', 'main_category', 'main_category2', 'company',
                  'industry', 'include_exclude', 'dept', 'division1',
                  'division2', 'title')
        labels = {
            'dept': _('Department'),
            'geo': _('Geographic Group'),
            'main_category': _('Main Category (F1)'),
            'main_category2': _('Secondary Category'),
            'division1': _('Sales Division 1'),
            'division2': _('Sales Division 2'),
        }
        widgets = {
            'dept': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'geo': forms.Select(
                attrs={'class': 'form-control'}
            ),
            'main_category': forms.Select(
                attrs={'class': 'form-control'}
            ),
            'main_category2': forms.Select(
                attrs={'class': 'form-control'}
            ),
            'company': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'industry': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'include_exclude': forms.Select(
                attrs={'class': 'form-control'}
            ),
            'division1': forms.Select(
                attrs={'class': 'form-control'}
            ),
            'division2': forms.Select(
                attrs={'class': 'form-control'}
            ),
            'title': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
        }

    def __init__(self, *args, **kwargs):
        try:
            filter_master_bool = kwargs.pop('filter_master_bool')
        except KeyError:
            filter_master_bool = True
        super(PersonalTerritorySelects, self).__init__(*args, **kwargs)
        if filter_master_bool:
            self.fields['include_exclude'] = forms.ChoiceField(
                choices = (('filter',
                            "Filter (exclude values that don't match)"),
                           ('add', 'Add to List'),
                           ('exclude', 'Exclude from list'),),
                widget=forms.Select(
                    attrs={'class': 'form-control'}
                ),
            )
        else:
            self.fields['include_exclude'] = forms.ChoiceField(
                choices = (('add', 'Add to List'),
                           ('exclude', 'Exclude from list'),),
                widget=forms.Select(
                    attrs={'class': 'form-control'}
                ),
            )
        del filter_master_bool
        set_field_html_name(self.fields['geo'], 'geo_peronal')
        set_field_html_name(self.fields['main_category'],
                            'main_category_peronal')
        set_field_html_name(self.fields['main_category2'],
                            'main_category2_personal')
        set_field_html_name(self.fields['company'], 'company_personal')
        set_field_html_name(self.fields['industry'], 'industry_personal')
        set_field_html_name(self.fields['include_exclude'],
                            'include_exclude_personal')
        set_field_html_name(self.fields['dept'], 'dept_personal')


class SearchForm(forms.Form):
    name = forms.CharField(label='Name',
                           max_length=100,
                           required=False,
                           widget=forms.TextInput(
                               attrs={'class': 'form-control'}
                           ))
    title = forms.CharField(label="Title",
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
    state_province = forms.ChoiceField(label='State/Province',
                                       required=False,
                                       initial='',
                                       choices=STATE_PROV_TUPLE,
                                       widget=forms.Select(
                                           attrs={'class': 'form-control'}
                                       ))
    past_customer = forms.ChoiceField(label='Past Customer',
                                      required=False,
                                      initial='',
                                      choices=(('', 'Any'),
                                               (True, 'Yes'),
                                               (False, 'No'),),
                                      widget=forms.Select(
                                          attrs={'class': 'form-control'}
                                      ))
    date_modified = forms.DateField(label='Modified on or After',
                                    required=False,
                                    widget=forms.TextInput(
                                        attrs={'class': 'form-control',
                                               'placeholder': 'yyyy-mm-dd'}
                                    ))


class SelectMyTerritoryForm(forms.ModelForm):

    class Meta:
        model = EventAssignment
        fields = ('event',)
        labels = {
            'event': _('Select Event')
        }
        widgets = {
            'event': forms.Select(
                attrs={'class': 'form-control'}
            ),
        }
