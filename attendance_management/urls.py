
from django.urls import path
from . import views
from .dashboard_views import attendance_dashboard

urlpatterns = [
    path('dashboard/', attendance_dashboard, name='attendance_dashboard'),
    path('attendance/', views.attendance_list, name='attendance_list'),
    path('attendance/add/', views.attendance_create, name='attendance_create'),
    path('get-today-attendance/', views.get_today_attendance, name='get_today_attendance'),  # ✅ this line is OK now
        path('employee/mark-attendance/', views.employee_attendance_create, name='employee_attendance_create'),
    path('employee/attendance/list/', views.employee_attendance_list, name='employee_attendance_list'),

    path('attendance/edit/<int:pk>/', views.attendance_edit, name='attendance_edit'),

]
