from django.db import models
from masters.models import Department

class Report(models.Model):
    REPORT_TYPE_CHOICES = [
        ('attendance', 'Attendance'),
        ('payroll', 'Payroll'),
        ('attrition', 'Attrition'),
        ('performance', 'Performance'),
    ]
    name = models.CharField(max_length=100)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='reports/')
