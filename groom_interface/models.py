from django.db import models
from userauth.models import User
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from pet_owner.models import Feedback


# Create your models here.
class Service(models.Model):
    groomer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="services")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0, message="Price cannot be less than 0.")]
    )
    availability = models.BooleanField(default=True)
    image = models.ImageField(upload_to='services/', blank=True, null=True)
    pet_type = models.CharField(max_length=100, help_text="E.g., Dog, Cat, Rabbit, Bird")  # Updated field

    def __str__(self):
        return f"{self.name} - {self.pet_type} - {self.groomer.username}"



class GroomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="groomer_profile")
    bio = models.TextField(max_length=500, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='groomer_profiles/', blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    experience_years = models.PositiveIntegerField(default=0,
        validators=[MinValueValidator(0, message="Experience years cannot be less than 0.")]
    )
    services_offered = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"



class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ]
    
    groomer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="appointments")
    pet_owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owner_appointments")
    service = models.ForeignKey('Service', on_delete=models.CASCADE)
    date_time = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True)  # Add this field

    def __str__(self):
        return f"{self.service.name} - {self.date_time.strftime('%Y-%m-%d %H:%M')}"


class Response(models.Model):
    # Using string reference for Feedback to avoid circular import
    feedback = models.OneToOneField('pet_owner.Feedback', on_delete=models.CASCADE, related_name='response')
    groomer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='responses')
    response_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Response by {self.groomer.username} to feedback for {self.feedback.service.name}"


