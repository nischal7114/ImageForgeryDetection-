from django import forms
from .models import CaseImage

class CaseImageForm(forms.ModelForm):
    class Meta:
        model = CaseImage
        fields = ['image']

class ImageVerificationForm(forms.Form):
    image = forms.ImageField(label="Upload Image for Verification")