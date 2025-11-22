from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .dashboard_views import dashboard, home_redirect
from masters.views import login_view, logout_view


urlpatterns = [
    path('admin/', admin.site.urls),
    path('masters/', include('masters.urls')),
    path('employees/', include('employee_management.urls')),
    path('leaves/', include('leave_management.urls')),
    path('attendance/', include('attendance_management.urls')),
    path('payroll/', include('payroll_management.urls')),
    path('performance/', include('performance_management.urls')),
    path('recruitment/', include('recruitment.urls')),
    path('chatbot/', include('chatbot.urls')),
    path('notifications/', include('notifications.urls')),
    path('reports/', include('reports.urls')),

    # ✅ custom authentication
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    path('dashboard/', dashboard, name='dashboard'),
    path('', home_redirect, name='home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
