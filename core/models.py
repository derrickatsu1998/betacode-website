from django.db import models

# Create your models here.from django.db import models

class ReceivedBugReport(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    page_url = models.URLField(blank=True, null=True)
    reporter_name = models.CharField(max_length=255, blank=True, null=True)
    screenshot_url = models.URLField(blank=True, null=True)
    voice_note_url = models.URLField(blank=True, null=True)
    status = models.CharField(max_length=50, default='open')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.status}"