from django.db import models
from django.contrib.auth.models import User

class Posting(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Closed', 'Closed'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    deadline = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')
    organization = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
<<<<<<< HEAD
    
=======

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
>>>>>>> feature/duplicate_validation
