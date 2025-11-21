
from django.urls import path
from .import views
from .dashboard_views import employee_dashboard

urlpatterns = [
    path('dashboard/', employee_dashboard, name='employee_dashboard'),
    path('departments/', views.department_list, name='department_list'),
    path('departments/add/', views.department_create, name='department_create'),
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/add/', views.employee_create, name='employee_create'),

    path('employees/<int:pk>/view/', views.employee_view, name='employee_view'),
    path('employees/<int:pk>/edit/', views.employee_edit, name='employee_edit'),
    path('employees/<int:pk>/delete/', views.employee_delete, name='employee_delete'),

      path('', views.redirect_to_login),  # root → login
     path('login/', views.employee_login_view, name='employee_login_view'),
      path('set-passcode/', views.employee_set_passcode, name='employee_set_passcode'),
     path('password-reset/', views.employee_password_reset_view, name='employee_password_reset_view'),

    path('logout/', views.employee_logout, name='employee_logout'),
    
    path('dashboard-view/', views.employee_dashboard_view, name='employee_dashboard_view'),  # alternate dashboard
    path('profile/', views.employee_profile, name='employee_profile'), 

    path("calendar/", views.employee_calendar, name="employee_calendar"),
     path("leave/create/", views.employee_leave_create, name="employee_leave_create"),
      path("leave/edit/<int:leave_id>/", views.employee_leave_create, name="employee_leave_edit"),


      path("leaves/", views.employee_leave_list, name="employee_leave_list"),
    path("leaves/<int:leave_id>/approve/", views.leave_approve, name="leave_approve"),
    path("leaves/<int:leave_id>/reject/", views.leave_reject, name="leave_reject"),


    path("performance/", views.employee_performance, name="employee_performance"),


    path('employee/dashboard2/', views.employee_dashboard_view2, name='employee_dashboard2'),


     path('my-payslips/', views.employee_payslips, name='employee_payslips'),
    path('payslip/download/<int:payslip_id>/', views.download_payslip, name='download_payslip'),

     path("employee/jobs/", views.employee_job_list, name="employee_job_list"),
     path("upload-resume/<int:requisition_id>/", views.upload_resume, name="upload_resume")
]
