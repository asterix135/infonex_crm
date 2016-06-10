from django import forms
from django.contrib.auth.models import User

from .models import *


class PersonUpdateForm(forms.ModelForm):

    class Meta:
        model = Person
        fields = ('name', 'title', 'company', 'url', 'phone', 'phone_main',
                  'do_not_call', 'email', 'do_not_email', 'industry', 'dept',
                  'city',)
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
            'phone_main': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'email': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'industry': forms.Textarea(
                attrs={'class': 'form-control',
                       'rows': '3'}
            ),
            'dept': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
        }


class PersonCategoryUpdateForm(forms.ModelForm):

    class Meta:
        model = Person
        fields = ('dept', 'geo', 'main_category', 'main_category2',
                  'division1', 'division2',)
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


class PersonChangesForm(forms.ModelForm):

    class Meta:
        model = Changes
        fields = ('name', 'title')


class PersonDeleteConfirmForm(forms.ModelForm):

    class Meta:
        model = Person
        fields = ('name', 'title')


class ListSelectForm(forms.ModelForm):
    event = forms.ModelChoiceField(queryset=Event.objects.all(),
                                   empty_label=None,
                                   widget=forms.Select(
                                       attrs={'class': 'form-control'}
                                   ))
    employee = forms.ModelChoiceField(queryset=User.objects.all(),
                                      empty_label=None,
                                      widget=forms.Select(
                                          attrs={'class': 'form-control'}
                                      ))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee'].initial = 'override'
        self.fields['event'].queryset = \
            Event.objects.all().order_by('date_begins').reverse()[:25]

    class Meta:
        model = ListSelection
        fields = ('geo', 'main_category', 'main_category2', 'industry',
                  'division1', 'division2', 'company', 'include_exclude')
        widgets = {
            'geo': forms.Select(
                attrs={'class': 'form-control'}
            ),
            'main_category': forms.Select(
                attrs={'class': 'form-control'}
            ),
            'main_category2': forms.Select(
                attrs={'class': 'form-control'}
            ),
            'industry': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'division1': forms.Select(
                attrs={'class': 'form-control'}
            ),
            'division2': forms.Select(
                attrs={'class': 'form-control'}
            ),
            'company': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'include_exclude': forms.Select(
                attrs={'class': 'form-control'}
            ),
        }


class TerritoryForm(forms.ModelForm):

    class Meta:
        model = ListSelection
        fields = ('employee', 'event')
        widgets = {
            'employee': forms.Select(
                attrs={'class': 'form-control'}
            ),
            'event': forms.Select(
                attrs={'class': 'form-control'}
            ),
        }


class FlagForm(forms.ModelForm):

    class Meta:
        model = PersonFlag
        fields = ('flag', 'follow_up_date')
        widgets = {
            'flag': forms.Select(
                attrs={'class': 'form-control'}
            )
        }


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
    date_modified = forms.DateField(label='Modified on or After',
                                    required=False,
                                    widget=forms.TextInput(
                                        attrs={'class': 'form-control',
                                               'placeholder': 'yyyy-mm-dd'}
                                    ))
