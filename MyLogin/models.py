from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    ROLE_CHOICES = [
        ('Student', 'Student'),
        ('Organization', 'Organization'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Student')
    org_name = models.CharField(max_length=255, blank=True, null=True)  # add this here

    def __str__(self):
        return f"{self.user.username} ({self.role})"


