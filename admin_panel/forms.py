from django import forms
from pet_owner.models import PetType, PetBreed

class PetTypeForm(forms.ModelForm):
    class Meta:
        model = PetType
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter pet type'}),
        }

class BreedForm(forms.ModelForm):
    class Meta:
        model = PetBreed
        fields = ['pet_type', 'name']
        widgets = {
            'pet_type': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter breed name'}),
        }
