from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import GroomerProfile  # Import your profile model

User = get_user_model()  # Gets the custom User model

@receiver(post_save, sender=User)
def create_groomer_profile(sender, instance, created, **kwargs):
    """Creates a GroomerProfile when a groomer user is created."""
    if created and instance.role == "groomer":
        GroomerProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_groomer_profile(sender, instance, **kwargs):
    """Ensures the profile is saved when the User is updated."""
    if hasattr(instance, 'groomer_profile'):  # Check if profile exists
        instance.groomer_profile.save()
