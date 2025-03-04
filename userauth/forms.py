from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User
from django.core.validators import MinLengthValidator
from django.core.validators import RegexValidator



phone_number_validator = RegexValidator(
    regex=r'^[6-9]\d{9}$',
    message='Phone number must start with 6, 7, 8, or 9 and be 10 digits long.'
)


# Signup Form
class SignupForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}),
        help_text=""
    )
    phone_number = forms.CharField(
         required=True,
        max_length=10,
        validators=[
            MinLengthValidator(10),
            phone_number_validator  # Enforce 6-9 start here
        ],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your Phone number'}),
        help_text="Enter a 10-digit phone number starting with 6, 7, 8, or 9."
    )
    first_name = forms.CharField(
        required=True,
        max_length=15,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter you firstname'}),
        help_text=""
    )
    last_name = forms.CharField(
        required=True,
        max_length=15,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter you lastname'}),
        help_text=""
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose a username'}),
        help_text=""
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Create a password'}),
        help_text="",
        label="password"
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm your password'}),
        help_text="",
        label="confirm your password"
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name','username', 'email', 'password1', 'password2', 'role', 'phone_number']

# Login Form
class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your username'}),
        help_text=""
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password'}),
        help_text=""
    )
