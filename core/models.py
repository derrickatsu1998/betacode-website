from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

# ==========================================
# 1. BUG REPORT MODEL
# ==========================================
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
    
    # New fields for ticketing
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Open')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_bugs')
    developer_notes = models.TextField(blank=True, null=True)
    is_user_notified = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.status}"


# ==========================================
# 2. DEVELOPER PROFILE MODEL
# ==========================================
class DeveloperProfile(models.Model):
    ROLE_CHOICES = (
        ('admin', 'System Admin'),
        ('lead', 'Lead Developer'),
        ('dev', 'Software Engineer'),
        ('tester', 'QA / Tester'),
    )
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='developer_profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='dev')
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

# Automatically create a profile when a User is created
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_developer_profile(sender, instance, created, **kwargs):
    if created:
        DeveloperProfile.objects.get_or_create(user=instance)


# ==========================================
# 3. CHAT MESSAGE MODEL
# ==========================================
class ChatMessage(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.sender.username}: {self.message[:20]}"