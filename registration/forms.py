from django import forms
from django.contrib.auth.models import User

from .models import *
from crm.models import Event


class DelegateForm(forms.ModelForm):
    class Meta:
        model = Registrants
        fields = ('first_name', 'last_name', 'company')
        widgets = {
            'first_name': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'last_name': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'company': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            # 'postal_code': forms.TextInput(
            #     attrs={'class': 'form-control'}
            # ),
        }

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
    postal_code = forms.CharField(label='Company',
                                  max_length=100,
                                  required=False,
                                  widget=forms.TextInput(
                                      attrs={'class': 'form-control'}
                                  ))

    def __init__(self, *args, **kwargs):
        super(NewDelegateSearchForm, self).__init__(*args, **kwargs)
        self.fields['event'] = forms.ChoiceField(
            label='Select Conference',
            required=False,
            initial='',
            choices=(('e', 'f'), ('g', 'h')),
            widget=forms.Select(
                attrs={'class': 'form-control'}
            )
        )
