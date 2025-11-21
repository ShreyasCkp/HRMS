from django.db import models

class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    def __str__(self):
        return self.name

class JobRole(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    def __str__(self):
        return self.name

class LeaveType(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    default_balance = models.IntegerField(default=0)
    def __str__(self):
        return self.name

class PerformanceKPI(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    max_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    goal_threshold = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,  # minimum required to achieve the KPI
        help_text="Minimum score required to mark this goal as achieved"
    )
    review_frequency_days = models.IntegerField(
        default=90,  # e.g., review every 90 days
        help_text="Number of days after which review is due"
    )

    def __str__(self):
        return f"{self.name} (Max: {self.max_score}, Threshold: {self.goal_threshold})"


class InterviewRound(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    def __str__(self):
        return self.name

# Advanced: Workspace and OfficeEvent
class Workspace(models.Model):
    WORKSPACE_TYPE_CHOICES = [
        ('cabin', 'Cabin'),
        ('conference', 'Conference Room'),
        ('meeting', 'Meeting Room'),
    ]
    name = models.CharField(max_length=100)
    workspace_type = models.CharField(max_length=20, choices=WORKSPACE_TYPE_CHOICES)
    capacity = models.IntegerField()
    is_available = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.name} ({self.get_workspace_type_display()})"

class OfficeEvent(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=100)
    def __str__(self):
        return f"{self.title} on {self.date} at {self.location}"
from django.db import models

class UserCustom(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)  # still plain text for now

    # ➕ New fields to support login flow
    wrong_attempts = models.IntegerField(default=0)
    is_locked = models.BooleanField(default=False)
    passcode = models.CharField(max_length=4, blank=True, null=True)
    passcode_set = models.BooleanField(default=False)

    def __str__(self):
        return self.username

    # Method to return a full name (for now it just returns the username)
    def get_full_name(self):
        return self.username  # Returns username as the full name for now




# masters/models.py
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class RecentActivity(models.Model):
    ACTION_CHOICES = [
        ("created", "Created"),
        ("updated", "Updated"),
        ("deleted", "Deleted"),
        ("viewed", "Viewed"),
    ]

    # generic relation to either Employee or UserCustom (or any other user-like model)
    user_content_type = models.ForeignKey(
        ContentType, on_delete=models.SET_NULL, null=True, blank=True
    )
    user_object_id = models.PositiveIntegerField(null=True, blank=True)
    user = GenericForeignKey("user_content_type", "user_object_id")

    action = models.CharField(max_length=100, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=50)
    object_id = models.PositiveIntegerField()
    object_repr = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    @property
    def display_name(self):
        """
        Read-only computed name for templates.
        - Employee objects are expected to have `.name`
        - UserCustom objects are expected to have `.username` (optionally `.full_name`)
        - fallback to `str(self.user)` or 'System'
        """
        if self.user:
            # Employee-like
            if hasattr(self.user, "name"):
                return getattr(self.user, "name") or str(self.user)
            # UserCustom / Django User
            if hasattr(self.user, "username"):
                return getattr(self.user, "full_name", None) or self.user.username
            return str(self.user)
        return "System"

    def __str__(self):
        return f"{self.model_name} {self.action} by {self.display_name} at {self.timestamp:%Y-%m-%d %H:%M:%S}"
