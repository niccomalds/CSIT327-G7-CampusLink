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
    
    OPPORTUNITY_TYPE_CHOICES = [
        ('assistantship', 'Assistantship'),
        ('volunteer', 'Volunteer'),
        ('internship', 'Internship'),
        ('job', 'Job'),
        ('scholarship', 'Scholarship'),
        ('events', 'Events'),
        ('sports', 'Sports'),
        ('leadership', 'Leadership'),
        ('other', 'Other'),
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
    
    # Add the opportunity_type field
    opportunity_type = models.CharField(
        max_length=20, 
        choices=OPPORTUNITY_TYPE_CHOICES, 
        default='other'
    )

    def __str__(self):
        return self.title

    def is_approved(self):
        """Check if posting is approved"""
        return self.approval_status == 'approved'

    def is_pending_review(self):
        """Check if posting is pending admin review"""
        return self.approval_status == 'pending'

    # Removed auto-approval logic - all postings now require manual admin approval
    
    @property
    def is_auto_approved(self):
        """Check if this posting was auto-approved"""
        return False  # No auto-approval anymore


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