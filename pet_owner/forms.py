# forms.py
from django import forms
from .models import PetOwnerProfile, Pet

class PetOwnerProfileForm(forms.ModelForm):
    class Meta:
        model = PetOwnerProfile
        fields = ['phone_number', 'address', 'profile_picture']

class PetForm(forms.ModelForm):
    class Meta:
        model = Pet
        fields = ['name', 'breed', 'age', 'weight', 'gender', 'grooming_preferences', 'health_information', 'pet_picture']