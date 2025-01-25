from django.db import models
from userauth.models import User

# Create your models here.
class Service(models.Model):
    groomer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="services")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    availability = models.BooleanField(default=True)
    image = models.ImageField(upload_to='services/', blank=True, null=True)  # New field for image

    def __str__(self):
        return f"{self.name} - {self.groomer.username}"



class GroomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="groomer_profile")
    bio = models.TextField(max_length=500, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='groomer_profiles/', blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    experience_years = models.IntegerField(default=0)
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
    
    def __str__(self):
        return f"{self.service.name} - {self.date_time.strftime('%Y-%m-%d %H:%M')}"

