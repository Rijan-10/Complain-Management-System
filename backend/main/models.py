from django.db import models
from django.contrib.auth.models import User

import secrets
import string


def generate_complaint_id():
    alphabet = string.ascii_uppercase + string.digits
    return 'CMP-' + ''.join(secrets.choice(alphabet) for _ in range(8))


class Complaint(models.Model):
    CATEGORY_CHOICES = [
        ('road_pothole', 'Road Pothole'),
        ('garbage', 'Garbage'),
        ('drainage', 'Drainage'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected'),
    ]
    complaint_id = models.CharField(max_length=20, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='complaints')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField()
    landmark = models.CharField(max_length=200, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def reporter_name(self):
        if self.is_anonymous:
            return 'Anonymous'
        return self.user.email

    def save(self, *args, **kwargs):
        if not self.complaint_id:
            self.complaint_id = generate_complaint_id()
            while Complaint.objects.filter(complaint_id=self.complaint_id).exists():
                self.complaint_id = generate_complaint_id()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.complaint_id


class ComplaintImage(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='images')
    image_url = models.URLField(max_length=500, default='', blank=True)

    def __str__(self):
        return self.image_url


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


class PasswordResetRequest(models.Model):
    PENDING = 'pending'
    COMPLETED = 'completed'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (COMPLETED, 'Completed'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='reset_requests')
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    requested_password = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} ({self.status})"
