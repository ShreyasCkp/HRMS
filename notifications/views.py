from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from .models import Notification

def mark_as_read_and_redirect(request, notification_id):
    # Get the notification or 404 if not found
    notification = get_object_or_404(Notification, id=notification_id)

    # Mark the notification as read
    notification.is_read = True  # Make sure you have this field in your Notification model
    notification.save()

    # ✅ Redirect to the leave dashboard page after marking as read
    return redirect(reverse("leave_dashboard"))
