from django import forms

class UploadFileForm(forms.Form):
    marketing_file = forms.FileField(
        widget=forms.FileInput(
            attrs={'style': 'display: none;'}
        )
    )
