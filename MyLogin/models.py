from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Profile(models.Model):
    ROLE_CHOICES = (
        ('Student', 'Student'),
        ('Organization', 'Organization'),
    )

    # Verification Status Choices
    VERIFICATION_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
        ('unverified', 'Unverified'),
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
    
    verification_status = models.CharField(
        max_length=20, 
        choices=VERIFICATION_STATUS_CHOICES, 
        default='unverified'
    )
    verification_documents = models.FileField(
        upload_to='verification_docs/', 
        blank=True, 
        null=True
    )
    institutional_email = models.EmailField(blank=True, null=True)
    verification_reason = models.TextField(blank=True, null=True)
    verified_at = models.DateTimeField(blank=True, null=True)
    verification_submitted_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

    def is_verified_organization(self):
        """Check if this profile is a verified organization"""
        return self.role == 'Organization' and self.verification_status == 'verified'
    
    def get_verification_badge(self):
        """Return HTML for verification badge"""
        if self.is_verified_organization():
            return '<span class="verified-badge" title="Verified Organization">✅ Verified</span>'
        return ''

    def submit_verification(self, documents, institutional_email):
        """Submit verification request"""
        self.verification_documents = documents
        self.institutional_email = institutional_email
        self.verification_status = 'pending'
        self.verification_submitted_at = timezone.now()
        self.save()
