# smarthr_erp/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from .dashboard_views import dashboard
from masters.views import login_view, logout_view

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # Auth
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),

    # App modules
    path("masters/", include("masters.urls")),
    path("employees/", include("employee_management.urls")),
    path("leaves/", include("leave_management.urls")),
    path("attendance/", include("attendance_management.urls")),
    path("payroll/", include("payroll_management.urls")),   # ⬅ will use your payroll_dashboard
    path("performance/", include("performance_management.urls")),
    path("recruitment/", include("recruitment.urls")),
    path("chatbot/", include("chatbot.urls")),
    path("notifications/", include("notifications.urls")),
    path("reports/", include("reports.urls")),

    # Main dashboard (protected by session_login_required in dashboard_views.py)
    path("dashboard/", dashboard, name="dashboard"),

    # Root URL → show login page (same view as /login/)
    path("", login_view, name="home"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
