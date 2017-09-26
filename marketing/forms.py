from django import forms

from crm.models import Changes, Person


class ChangesDetailForm(forms.ModelForm):

    class Meta:
        model = Changes
        fields = '__all__'


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


class UploadFileForm(forms.Form):
    marketing_file = forms.FileField(
        widget=forms.FileInput(
            attrs={'style': 'display: none;'}
        )
    )
