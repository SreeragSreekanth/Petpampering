# models.py
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.apps import apps  # Import apps module


class PetOwnerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pet_owner_profile')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class Pet(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pets')
    name = models.CharField(max_length=100)
    pet_type = models.CharField(max_length=100, help_text="E.g., Dog, Cat, Rabbit, Bird")  # New field for pet type
    breed = models.CharField(max_length=100, blank=True, null=True)
    age = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(30)])
    weight = models.DecimalField(max_digits=5, decimal_places=2, help_text="Weight in kg")
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    grooming_preferences = models.TextField(blank=True, null=True)
    health_information = models.TextField(blank=True, null=True)
    pet_picture = models.ImageField(upload_to='pet_pics/', blank=True, null=True)

    def save(self, *args, **kwargs):
        self.pet_type = self.pet_type.strip().lower()  # Ensure lowercase and strip any spaces
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.pet_type} - {self.breed})"
    
    
class PetOwnerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pet_owner_profile')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
    
class CommunityPost(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    

class Reply(models.Model):
    post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name="replies")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reply by {self.user.username} on {self.post.title}"


class Feedback(models.Model):
    pet_owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # Use string reference for Service model
    service = models.ForeignKey('groom_interface.Service', on_delete=models.CASCADE,related_name='feedbacks')
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.pet_owner.username} for {self.service.name}"
