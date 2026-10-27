from django.db import models
from django.conf import settings

class ReceivedBugReport(models.Model):
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
        ('Closed', 'Closed'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    page_url = models.URLField(blank=True, null=True)
    reporter_name = models.CharField(max_length=255, blank=True, null=True)
    screenshot_url = models.URLField(blank=True, null=True)
    voice_note_url = models.URLField(blank=True, null=True)
    
    # NEW FIELDS
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Open')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_bugs')
    developer_notes = models.TextField(blank=True, null=True)
    is_user_notified = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.status}"