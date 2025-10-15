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


class Posting(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Closed', 'Closed'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    deadline = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')
    organization = models.ForeignKey(User, on_delete=models.CASCADE)  # link to Profile/Organization
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title