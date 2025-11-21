from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Attendance
from employee_management.models import Employee
from datetime import date, timedelta
from django.db.models import Avg


def attendance_dashboard(request):
    today = date.today()
    
    # Total present and absent for today
    total_present = Attendance.objects.filter(date=today, clock_in__isnull=False).count()
    total_absent = Employee.objects.filter(is_active=True).count() - total_present
    
    # Total late arrivals for today
    late_arrivals = Attendance.objects.filter(date=today, late_arrival=True).count()
    
    # Average work hours for today (clock-in and clock-out should both be present)
    avg_work_hours = Attendance.objects.filter(clock_in__isnull=False, clock_out__isnull=False).aggregate(avg=Avg('clock_out'))['avg'] or 0

    # Today's attendance records
    today_attendance = Attendance.objects.filter(date=today).select_related('employee')

    # Weekly Overview
    weekly_overview = []
    for i in range(7):
        day = today - timedelta(days=i)
        
        # Get present count for the day (only those who clocked in)
        present = Attendance.objects.filter(date=day, clock_in__isnull=False).count()
        
        # Get absent count for the day (all active employees minus those who were present)
        absent = Employee.objects.filter(is_active=True).count() - present
        
        # Calculate the percentage of present employees
        total_employees = Employee.objects.filter(is_active=True).count()
        present_percent = (present / total_employees * 100) if total_employees > 0 else 0
        
        # Append the data to the weekly overview list
        weekly_overview.append({
            'date': day,
            'present': present,
            'absent': absent,
            'present_percent': round(present_percent, 2),  # Round to 2 decimal places
        })
    
    # Reverse the list to display from Monday to Sunday
    weekly_overview.reverse()

    # Render the template with all required context data
    return render(request, 'attendance_dashboard.html', {
        'total_present': total_present,
        'total_absent': total_absent,
        'late_arrivals': late_arrivals,
        'avg_work_hours': avg_work_hours,
        'today_attendance': today_attendance,
        'weekly_overview': weekly_overview,
        'today_date': today,
    })
