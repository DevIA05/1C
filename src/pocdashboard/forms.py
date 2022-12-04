from django import forms

def validate_file_extension(value):
        if not value.name.endswith('.csv'):
            raise forms.ValidationError("Seul les fichiers CSV sont acceptés")

class CsvImportForm(forms.Form):
    csv_upload = forms.FileField(label='',validators=[validate_file_extension]) #widget=forms.FileInput(attrs={'accept': ".csv"}))