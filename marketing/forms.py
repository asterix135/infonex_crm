from django import forms

class UploadFileForm(forms.Form):
    marketing_file = forms.FileField(
        widget=forms.FileInput(
            attrs={'style': 'display: none;'}
        )
    )


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

    def _person_model_fields(self):
        return [('foo', 'foo'), ('bar', 'bar')]

    def __init__(self, *args, **kwargs):
        super(FieldSelectorForm, self).__init__(*args, **kwargs)
        self.fields['field_option'] = forms.ChoiceField(
            choices = self._person_model_fields,
            widget=forms.Select(
                attrs={'class': 'form-control pull-left'}
            )
        )
