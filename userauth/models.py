from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('owner', 'Pet Owner'),
        ('groomer', 'Groomer'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='owner')
    is_approved = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=10)  # New field added
    

    def __str__(self):
        return self.username
    



    

