from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    ROLE_CHOICES = (
        ('Student', 'Student'),
        ('Organization', 'Organization'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Student')
    org_name = models.CharField(max_length=255, blank=True, null=True)

    # MAIN PROFILE FIELDS
    full_name = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    academic_year = models.CharField(max_length=50, blank=True)
    major = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)

    # PROFILE IMAGE
    profile_picture = models.ImageField(upload_to='profile_pics/', default='default.jpg')

    def __str__(self):
        return f"{self.user.username} ({self.role})"
