# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import PetOwnerProfile

User = get_user_model()  # Gets the custom User model

@receiver(post_save, sender=User)
def create_pet_owner_profile(sender, instance, created, **kwargs):
    """Creates a PetOwnerProfile when a pet owner user is created."""
    if instance.role == "pet_owner":  
        if instance.is_approved:  # ✅ Create profile **only if approved**
            PetOwnerProfile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_pet_owner_profile(sender, instance, **kwargs):
    """Ensures the profile is saved when the User is updated."""
    if hasattr(instance, 'pet_owner_profile'):  # Check if profile exists
        instance.pet_owner_profile.save()