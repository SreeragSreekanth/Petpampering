# forms.py
from django import forms
from .models import *
from groom_interface.models import *
from datetime import datetime
from django.utils import timezone
from django.core.exceptions import ValidationError




class PetOwnerProfileForm(forms.ModelForm):
    class Meta:
        model = PetOwnerProfile
        fields = ['phone_number', 'address', 'profile_picture']

class PetForm(forms.ModelForm):
    class Meta:
        model = Pet
        fields = ['name', 'pet_type','breed', 'age', 'weight', 'gender', 'grooming_preferences', 'health_information', 'pet_picture']

class AppointmentForm(forms.ModelForm):
    pet = forms.ModelChoiceField(queryset=Pet.objects.none())  # Filter pets for the logged-in user
    date_time = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))

    class Meta:
        model = Appointment
        fields = ['pet', 'date_time', 'notes']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Get user from the view
        super().__init__(*args, **kwargs)
        if user:
            self.fields['pet'].queryset = Pet.objects.filter(owner=user)  # Filter pets for the current user

    def clean_date_time(self):
        date_time = self.cleaned_data.get('date_time')

        # Check if the date_time is in the past (Django backend validation)
        if date_time < timezone.now():
            raise ValidationError("You cannot book an appointment in the past!")

        # Additional validation to ensure the time slot is not already taken
        if Appointment.objects.filter(date_time=date_time).exists():
            raise ValidationError("This time slot is already booked. Please choose another time.")

        return date_time

class RescheduleAppointmentForm(forms.ModelForm):
    date_time = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))

    class Meta:
        model = Appointment
        fields = ['date_time']


class CommunityPostForm(forms.ModelForm):
    class Meta:
        model = CommunityPost
        fields = ['title', 'content']


class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ['content']


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['rating', 'comment']

    rating = forms.ChoiceField(
        choices=[(str(i), f"{i} Stars") for i in range(1, 6)],  # Dropdown for rating (1-5)
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    comment = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Write your feedback here...'}),
        required=False
    )
