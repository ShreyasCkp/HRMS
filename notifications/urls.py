from django.urls import path
from . import views
from .views import mark_as_read_and_redirect


urlpatterns = [
    path(
        "mark/<int:notification_id>/",
        views.mark_as_read_and_redirect,
        name="mark_as_read_and_redirect"
    ),
]
