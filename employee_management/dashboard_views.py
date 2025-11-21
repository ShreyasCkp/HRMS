from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Employee
from .models import Leave
from django.utils import timezone
from datetime import timedelta


def employee_dashboard(request):
    today = timezone.now().date()
    # Total employees
    total_employees = Employee.objects.count()
    # Active employees
    active_employees = Employee.objects.filter(is_active=True).count()
    # Employees currently on leave (today)
    on_leave_today = Leave.objects.filter(
        is_approved=True,
        start_date__lte=today,
        end_date__gte=today
    ).count()
    # New hires in last 30 days
    last_30_days = today - timedelta(days=30)
    new_hires = Employee.objects.filter(joining_date__gte=last_30_days).count()
    # Fetch all employees for table
    employees = Employee.objects.select_related('department', 'job_role').all()
    # Attach status to each employee
    for emp in employees:
        leave_today = Leave.objects.filter(
            employee=emp,
            is_approved=True,
            start_date__lte=today,
            end_date__gte=today
        ).exists()
        if leave_today:
            emp.status = 'On Leave'
        elif emp.is_active:
            emp.status = 'Active'
        else:
            emp.status = 'Inactive'
    return render(request, 'employee_dashboard.html', {
        'total_employees': total_employees,
        'active_employees': active_employees,
        'on_leave_today': on_leave_today,
        'new_hires': new_hires,
        'employees': employees,
    })