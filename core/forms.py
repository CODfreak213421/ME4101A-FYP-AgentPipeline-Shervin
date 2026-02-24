from core.models import datafile
from django import forms

class UploadedFileForm(forms.ModelForm):
    class Meta:
        model = datafile
        fields = ['name', 'upload']
        widgets = { 
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter file name', 'autocomplete': 'off'}),
            'upload': forms.FileInput(attrs={'class': 'form-control', 'id': 'fileInput'}),
        }

    def clean_upload(self):
        uploaded_file = self.cleaned_data.get('upload')
        if uploaded_file:
            if not uploaded_file.name.endswith('.csv'):
                raise forms.ValidationError("Only CSV files are allowed.")
        return uploaded_file