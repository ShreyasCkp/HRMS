from django.urls import path
from .dashboard_views import reports_dashboard
from django.http import HttpResponse

def export_reports(request):
    return HttpResponse('Reports export (PDF/Excel) coming soon.')

urlpatterns = [
    path('dashboard/', reports_dashboard, name='reports_dashboard'),
    path('export/', export_reports, name='reports_export'),
]
