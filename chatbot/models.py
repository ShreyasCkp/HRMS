from django.db import models
from django.utils import timezone

class EscalatedQuery(models.Model):
    user_id = models.CharField(max_length=100)  # optional: link to employee model if available
    message = models.TextField()
    department = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    is_resolved = models.BooleanField(default=False)
    response = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Escalated by {self.user_id} on {self.created_at.strftime('%Y-%m-%d %H:%M')}"
