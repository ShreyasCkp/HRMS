# masters/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.apps import apps
from .middleware import get_current_user

# list of model names to track (as strings)
TRACK_MODELS = {
    "Employee",
    "Leave",
    "Attendance",
    "Department",
    "Notification",
    "LeaveType",
    "LeaveRequest",
    "LeaveBalance",
    "JobRole",
    "PerformanceKPI",
    "UserCustom",
    "Payroll",
    "PerformanceReview",
    "PerformanceScore",
    "JobRequisition",
    "Applicant",
    "OfficeEvent",
}


def create_activity(user, action, instance):
    """
    Create a RecentActivity pointing to whatever `user` object is (Employee, UserCustom, Django User).
    If user is None we skip logging.
    """
    if not user:
        return

    RecentActivity = apps.get_model("masters", "RecentActivity")
    RecentActivity.objects.create(
        user_content_type=ContentType.objects.get_for_model(user),
        user_object_id=user.pk,
        action=action,
        model_name=instance.__class__.__name__,
        object_id=getattr(instance, "pk", 0),
        object_repr=str(instance)[:200],
    )


@receiver(post_save)
def model_saved(sender, instance, created, **kwargs):
    # only track configured model names
    if sender.__name__ not in TRACK_MODELS:
        return
    user = get_current_user()
    create_activity(user, "created" if created else "updated", instance)


@receiver(post_delete)
def model_deleted(sender, instance, **kwargs):
    if sender.__name__ not in TRACK_MODELS:
        return
    user = get_current_user()
    create_activity(user, "deleted", instance)
