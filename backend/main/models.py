from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('admin', 'Admin'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    phone = models.CharField(max_length=20, blank=True)
    full_name = models.CharField(max_length=100, blank=True)
    account_status = models.CharField(max_length=10, default='active')

    def __str__(self):
        return f"{self.user.email} ({self.role})"
