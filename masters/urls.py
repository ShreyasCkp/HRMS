from django.urls import path
from . import views

urlpatterns = [
     path('login/', views.login_view, name='login_view'),
    path('logout/', views.logout_view, name='logout_view'),
    path('set-passcode/', views.set_passcode, name='set_passcode'),
    path('password-reset/', views.password_reset_view, name='password_reset_view'),
    

     path('users/', views.user_list, name='user_list'),
    path('users/add/', views.user_form, name='user_form'),
    path('users/<int:user_id>/', views.user_view, name='user_view'),
    path('users/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:user_id>/delete/', views.user_delete, name='user_delete'),

    
      path('dashboard/', views.master_dashboard, name='master_dashboard'),
    path('departments/', views.department_list, name='department_list'),
    path('departments/add/', views.department_create, name='department_create'),

    path('departments/<int:pk>/view/', views.department_view, name='department_view'),
path('departments/<int:pk>/edit/', views.department_edit, name='department_edit'),
path('departments/<int:pk>/delete/', views.department_delete, name='department_delete'),



    path('jobroles/', views.jobrole_list, name='jobrole_list'),
    path('jobroles/add/', views.jobrole_create, name='jobrole_create'),
    path('masters/jobroles/edit/<int:pk>/', views.jobrole_edit, name='jobrole_edit'),

    # View a job role (read-only)
    path('masters/jobroles/view/<int:pk>/', views.jobrole_view, name='jobrole_view'),

    # Delete a job role
    path('masters/jobroles/delete/<int:pk>/', views.jobrole_delete, name='jobrole_delete'),


    path('leavetypes/', views.leavetype_list, name='leavetype_list'),
    path('leavetypes/add/', views.leavetype_create, name='leavetype_create'),



     path('leavetypes/edit/<int:pk>/', views.leavetype_edit, name='leavetype_edit'),
    path('leavetypes/view/<int:pk>/', views.leavetype_view, name='leavetype_view'),
    path('leavetypes/delete/<int:pk>/', views.leavetype_delete, name='leavetype_delete'),
    path('kpis/', views.kpi_list, name='kpi_list'),
    path('kpis/add/', views.kpi_create, name='kpi_create'),
     path('kpis/<int:pk>/', views.kpi_view, name='kpi_view'),
    path('kpis/<int:pk>/edit/', views.kpi_edit, name='kpi_edit'),
    path('kpis/<int:pk>/delete/', views.kpi_delete, name='kpi_delete'),
     path('interviewrounds/', views.interviewround_list, name='interviewround_list'),
    path('interviewrounds/add/', views.interviewround_create, name='interviewround_create'),
    path('interviewrounds/<int:pk>/view/', views.interviewround_view, name='interviewround_view'),
    path('interviewrounds/<int:pk>/edit/', views.interviewround_edit, name='interviewround_edit'),
    path('interviewrounds/<int:pk>/delete/', views.interviewround_delete, name='interviewround_delete'),
    
]
