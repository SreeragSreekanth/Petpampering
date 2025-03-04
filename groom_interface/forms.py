from django import forms
from .models import GroomerProfile, Service,Response
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError



class GroomerProfileForm(forms.ModelForm):
    class Meta:
        model = GroomerProfile
        fields = ['bio', 'profile_picture', 'location', 'experience_years', 'services_offered']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
            'services_offered': forms.Textarea(attrs={'rows': 3}),
            'experience_years': forms.NumberInput(),
        }
        
        def clean_experience_years(self):
            experience_years = self.cleaned_data.get('experience_years')
            if experience_years is not None and experience_years < 0:
                raise ValidationError("Experience years cannot be less than 0.")
            return experience_years

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'price', 'availability', 'image', 'pet_type']

        def clean_price(self):
            price = self.cleaned_data.get('price')
            if price is not None and price < 0:
                raise ValidationError("Price cannot be less than 0.")
            return price

class ResponseForm(forms.ModelForm):
    class Meta:
        model = Response
        fields = ['response_text']
        widgets = {
            'response_text': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }




