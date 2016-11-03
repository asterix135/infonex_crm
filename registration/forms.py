from django import forms
from django.contrib.auth.models import User
from django.utils import timezone

from .models import *
from crm.models import Event


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
