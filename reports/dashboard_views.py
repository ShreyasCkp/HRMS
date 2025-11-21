from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from employee_management.models import Employee
from leave_management.models import LeaveRequest
from payroll_management.models import Payroll
from performance_management.models import PerformanceReview
from .models import Report
from django.db.models import Sum

@login_required
def reports_dashboard(request):
    total_employees = Employee.objects.count()
    total_leaves = LeaveRequest.objects.count()
    total_payroll = Payroll.objects.aggregate(total=Sum('net_salary'))['total'] or 0
    employee_growth = 'Stable'  # Placeholder
    leave_trends = 'Increasing'  # Placeholder
    payroll_trends = 'Stable'  # Placeholder
    performance_trends = 'Improving'  # Placeholder
    recent_reports = Report.objects.order_by('-created_at')[:10]
    return render(request, 'reports_dashboard.html', {
        'total_employees': total_employees,
        'total_leaves': total_leaves,
        'total_payroll': total_payroll,
        'employee_growth': employee_growth,
        'leave_trends': leave_trends,
        'payroll_trends': payroll_trends,
        'performance_trends': performance_trends,
        'recent_reports': recent_reports,
    })
