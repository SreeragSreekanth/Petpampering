from django import forms
from .models import GroomerProfile, Service

class GroomerProfileForm(forms.ModelForm):
    class Meta:
        model = GroomerProfile
        fields = ['bio', 'profile_picture', 'location', 'experience_years', 'services_offered']

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'price', 'availability', 'image']
