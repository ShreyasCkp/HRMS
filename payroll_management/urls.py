from django.urls import path
from . import views
from .dashboard_views import payroll_dashboard
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('dashboard/', payroll_dashboard, name='payroll_dashboard'),
    path('payroll/records/', views.payroll_records, name='payroll_records'),

    path('', views.payroll_list, name='payroll_list'),
    path('add/', views.payroll_create, name='payroll_create'),
    path('process/', views.process_payroll, name='payroll_process'),
    path('export/', views.export_payroll, name='payroll_export'),
    path('tax/', views.tax_calculations, name='payroll_tax'),
    path('view/<int:pk>/', views.payroll_view, name='payroll_view'),
    path('edit/<int:pk>/', views.payroll_edit, name='payroll_edit'),
    path('generate-payslip/<int:pk>/', views.generate_payslip_download, name='generate_payslip'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
