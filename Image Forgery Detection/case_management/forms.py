from django import forms
from .models import Case

class CaseForm(forms.ModelForm):
    class Meta:
        model = Case
        fields = ['case_name', 'description', 'status']
        widgets = {
            'case_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter case name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4,
                'placeholder': 'Enter case description'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
        }