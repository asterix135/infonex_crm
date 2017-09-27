from django import forms
from django.utils.translation import ugettext_lazy as _

from crm.models import Changes, Person


class ChangesDetailForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ChangesDetailForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].disabled = True

    class Meta:
        model = Changes
        fields = ('name', 'title', 'company', 'phone',
                  'phone_main', 'email', 'do_not_call', 'do_not_email',
                  'city', 'dept', 'industry', 'geo', 'main_category',
                  'main_category2', 'division1', 'division2',)
        labels = {
            'industry': _('Industry Description'),
            'dept': _('Department'),
            'geo': _('Geographic Group'),
            'main_category': _('Main Category (F1)'),
            'main_category2': _('Secondary Category'),
            'division1': _('Main Sales Division'),
            'division2': _('Secondary Sales Division'),
        }
        widgets = {
            'name': forms.TextInput(
                attrs={'class': 'form-control change-field'},
            ),
            'title': forms.TextInput(
                attrs={'class': 'form-control change-field'}
            ), #
            'company': forms.TextInput(
                attrs={'class': 'form-control change-field'}
            ), #
            'phone': forms.TextInput(
                attrs={'class': 'form-control change-field'}
            ), #
            'phone_main': forms.TextInput(
                attrs={'class': 'form-control change-field'}
            ), #
            'email': forms.TextInput(
                attrs={'class': 'form-control change-field'}
            ), #
            'do_not_call': forms.CheckboxInput(
                attrs={'class': 'form-control change-field'}
            ), #
            'do_not_email': forms.CheckboxInput(
                attrs={'class': 'form-control change-field'}
            ), #
            'city': forms.TextInput(
                attrs={'class': 'form-control change-field'}
            ), #
            'dept': forms.TextInput(
                attrs={'class': 'form-control change-field'}
            ), #
            'industry': forms.Textarea(
                attrs={'class': 'form-control change-field',
                       'rows': '3'}
            ), #
            'geo': forms.Select(
                attrs={'class': 'form-control change-field'}
            ), #
            'main_category': forms.Select(
                attrs={'class': 'form-control change-field'}
            ), #
            'main_category2': forms.Select(
                attrs={'class': 'form-control change-field'}
            ), #
            'division1': forms.Select(
                attrs={'class': 'form-control change-field'}
            ), #
            'division2': forms.Select(
                attrs={'class': 'form-control change-field'}
            ), #
        }


class FieldSelectorForm(forms.Form):
    field_option = forms.ChoiceField(
        label='database_field',
        required=False,
        initial='',
        choices=[('f1', 'f1'), ('name', 'name')],
        widget=forms.Select(
            attrs={'class': 'form-control pull-left'}
        )
    )
    import_first_row = forms.BooleanField(
        label='Do not import first row (because they are headers)',
        initial=True,
        widget=forms.CheckboxInput(
            attrs={'class': 'form-control'}
        )
    )

    def _person_model_fields(self):
        person_fields = [f.name for f in Person._meta.get_fields()]
        fields_to_remove = ['date_created', 'created_by', 'modified_by']
        for fieldname in person_fields:
            if fieldname == 'id':
                break
            else:
                fields_to_remove.append(fieldname)
        field_list = [x for x in person_fields if x not in fields_to_remove]
        field_list.insert(0, '')
        field_list.insert(1, 'f1-category-split')
        field_list = sorted(field_list)
        return tuple(zip(field_list, field_list))

    def __init__(self, *args, **kwargs):
        # pop kwargs before super
        super(FieldSelectorForm, self).__init__(*args, **kwargs)
        self.fields['field_option'] = forms.ChoiceField(
            choices = self._person_model_fields,
            initial='',
            widget=forms.Select(
                attrs={'class': 'form-control pull-left'}
            )
        )


class PersonDetailForm(forms.ModelForm):

    class Meta:
        model = Person
        fields = ('name', 'title', 'company', 'phone',
                  'phone_main', 'email', 'do_not_call', 'do_not_email',
                  'city', 'dept', 'industry', 'geo', 'main_category',
                  'main_category2', 'division1', 'division2',)
        labels = {
            'industry': _('Industry Description'),
            'dept': _('Department'),
            'geo': _('Geographic Group'),
            'main_category': _('Main Category (F1)'),
            'main_category2': _('Secondary Category'),
            'division1': _('Main Sales Division'),
            'division2': _('Secondary Sales Division'),
        }
        widgets = {
            'name': forms.TextInput(
                attrs={'class': 'form-control'},
            ),
            'title': forms.TextInput(
                attrs={'class': 'form-control'}
            ), #
            'company': forms.TextInput(
                attrs={'class': 'form-control'}
            ), #
            'phone': forms.TextInput(
                attrs={'class': 'form-control'}
            ), #
            'phone_main': forms.TextInput(
                attrs={'class': 'form-control'}
            ), #
            'email': forms.TextInput(
                attrs={'class': 'form-control'}
            ), #
            'do_not_call': forms.CheckboxInput(
                attrs={'class': 'form-control'}
            ), #
            'do_not_email': forms.CheckboxInput(
                attrs={'class': 'form-control'}
            ), #
            'city': forms.TextInput(
                attrs={'class': 'form-control'}
            ), #
            'dept': forms.TextInput(
                attrs={'class': 'form-control'}
            ), #
            'industry': forms.Textarea(
                attrs={'class': 'form-control',
                       'rows': '3'}
            ), #
            'geo': forms.Select(
                attrs={'class': 'form-control'}
            ), #
            'main_category': forms.Select(
                attrs={'class': 'form-control'}
            ), #
            'main_category2': forms.Select(
                attrs={'class': 'form-control'}
            ), #
            'division1': forms.Select(
                attrs={'class': 'form-control'}
            ), #
            'division2': forms.Select(
                attrs={'class': 'form-control'}
            ), #
        }


class UploadFileForm(forms.Form):
    marketing_file = forms.FileField(
        widget=forms.FileInput(
            attrs={'style': 'display: none;'}
        )
    )
