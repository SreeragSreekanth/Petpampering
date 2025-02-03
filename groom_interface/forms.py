from django import forms
from .models import GroomerProfile, Service,Response

class GroomerProfileForm(forms.ModelForm):
    class Meta:
        model = GroomerProfile
        fields = ['bio', 'profile_picture', 'location', 'experience_years', 'services_offered']
class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'price', 'availability', 'image', 'pet_type']

class ResponseForm(forms.ModelForm):
    class Meta:
        model = Response
        fields = ['response_text']
        widgets = {
            'response_text': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }




