
from django.urls import path
from . import views
from .dashboard_views import leave_dashboard

urlpatterns = [
    path('dashboard/', leave_dashboard, name='leave_dashboard'),
    path('leaves/', views.leave_list, name='leave_list'),
    path('leaves/add/', views.leave_create, name='leave_create'),
    path('leave-types/', views.leave_type_list, name='leave_type_list'),
    path('leave-types/add/', views.leave_type_create, name='leave_type_create'),
]
