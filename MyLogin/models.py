from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Profile(models.Model):
    ROLE_CHOICES = (
        ('Student', 'Student'),
        ('Organization', 'Organization'),
    )

    VERIFICATION_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
        ('unverified', 'Unverified'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Student')

    # BASIC INFO
    org_name = models.CharField(max_length=255, blank=True, default="")
    full_name = models.CharField(max_length=200, blank=True, default="")
    contact_email = models.EmailField(blank=True, default="")
    phone = models.CharField(max_length=20, blank=True, default="")
    academic_year = models.CharField(max_length=50, blank=True, default="")
    major = models.CharField(max_length=100, blank=True, default="")
    bio = models.TextField(blank=True, default="")

    # PROFILE & LOGO
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    org_logo = models.ImageField(upload_to="org_logos/", null=True, blank=True)

    # ORG DETAILS (US-76)
    description = models.TextField(null=True, blank=True)
    mission = models.TextField(null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    department = models.CharField(max_length=255, null=True, blank=True)

    # SOCIAL LINKS
    social_facebook = models.URLField(null=True, blank=True)
    social_instagram = models.URLField(null=True, blank=True)
    social_linkedin = models.URLField(null=True, blank=True)

    # CONTACT DETAILS
    contact_phone = models.CharField(max_length=20, null=True, blank=True)

    # VISIBILITY SETTINGS
    is_public = models.BooleanField(default=True)

    # VERIFICATION FIELDS
    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS_CHOICES,
        default='unverified'
    )
    verification_documents = models.FileField(upload_to='verification_docs/', null=True, blank=True)
    institutional_email = models.EmailField(null=True, blank=True)
    verification_reason = models.TextField(null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    verification_submitted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

    def is_verified_organization(self):
        return self.role == 'Organization' and self.verification_status == 'verified'

    def get_verification_badge(self):
        if self.is_verified_organization():
            return '<span class="verified-badge">✅ Verified</span>'
        return ''


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('posting_approved', 'Posting Approved'),
        ('posting_rejected', 'Posting Rejected'),
        ('verification_approved', 'Verification Approved'),
        ('verification_rejected', 'Verification Rejected'),
    )
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_notifications')
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=timezone.now)
    related_posting = models.ForeignKey('Myapp.Posting', on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.title} - {self.recipient.username}"
    
    class Meta:
        ordering = ['-timestamp']