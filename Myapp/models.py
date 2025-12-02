from django.db import models
from django.contrib.auth.models import User

class Posting(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Closed', 'Closed'),
    ]
    
    APPROVAL_STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    deadline = models.DateField()
    tags = models.CharField(max_length=255, blank=True, default="")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')
    organization = models.ForeignKey(
    User,
    on_delete=models.CASCADE,
    related_name='myapp_postings'
)

    created_at = models.DateTimeField(auto_now_add=True)

    approval_status = models.CharField(
        max_length=20, 
        choices=APPROVAL_STATUS_CHOICES, 
        default='pending'
    )
    approved_at = models.DateTimeField(blank=True, null=True)
    approved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        related_name='approved_postings'
    )
    rejection_reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title

    def is_approved(self):
        """Check if posting is approved"""
        return self.approval_status == 'approved'

    def is_pending_review(self):
        """Check if posting is pending admin review"""
        return self.approval_status == 'pending'

    def save(self, *args, **kwargs):
        """Override save to implement auto-approval for verified organizations"""
        # Check if this is a new posting (not yet saved)
        is_new = self._state.adding
        
        # Auto-approve if organization is verified and it's a new posting
        if is_new and hasattr(self.organization, 'profile'):
            if self.organization.profile.is_verified_organization():
                self.approval_status = 'approved'
                # You could also set approved_by to system or leave null
                
        super().save(*args, **kwargs)
    
    @property
    def is_auto_approved(self):
        """Check if this posting was auto-approved"""
        return (self.approval_status == 'approved' and 
                not self.approved_by and 
                hasattr(self.organization, 'profile') and
                self.organization.profile.is_verified_organization())

class Application(models.Model):
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    ]
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    posting = models.ForeignKey(Posting, on_delete=models.CASCADE, related_name='applications')
    resume = models.FileField(upload_to='resumes/')
    note = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'posting']
    
    def __str__(self):
        return f"{self.student.email} - {self.posting.title}"