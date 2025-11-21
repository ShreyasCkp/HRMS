from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from datetime import date, datetime, time
from calendar import monthrange
import calendar

from .models import Attendance
from .forms import AttendanceForm, EmployeeAttendanceForm
from employee_management.models import Employee
from django.db.models.functions import ExtractYear


def attendance_list(request):
    records = Attendance.objects.select_related('employee').all()
    return render(request, 'attendance_management/attendance_list.html', {'records': records})


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date
from .forms import AttendanceForm
from .models import Attendance

def attendance_create(request):
    today = date.today()

    if request.method == 'POST':
        form = AttendanceForm(request.POST)

        if form.is_valid():
            employee = form.cleaned_data['employee']
            clock_in = form.cleaned_data['clock_in']
            clock_out = form.cleaned_data['clock_out']
            early_exit = form.cleaned_data['early_exit']

            attendance, created = Attendance.objects.get_or_create(
                employee=employee,
                date=today,
                defaults={
                    'clock_in': clock_in,
                    'clock_out': clock_out,
                    'early_exit': early_exit,
                }
            )

            if not created:
                if clock_in:
                    attendance.clock_in = clock_in
                if clock_out:
                    attendance.clock_out = clock_out
                attendance.early_exit = early_exit
                attendance.save()
                messages.success(request, f"{employee}’s attendance updated successfully.")
            else:
                messages.success(request, f"{employee}’s attendance recorded successfully.")

            return redirect('attendance_list')
    else:
        form = AttendanceForm()

    return render(request, 'attendance_management/attendance_form.html', {'form': form})



# views.py

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from datetime import date
from .models import Attendance

@login_required
def get_today_attendance(request):
    # Get employee_id from query parameters
    employee_id = request.GET.get('employee_id')

    if not employee_id:
        return JsonResponse({'error': 'Employee ID is required'}, status=400)

    today = date.today()

    try:
        # Fetch the attendance for the given employee and today's date
        attendance = Attendance.objects.get(employee_id=employee_id, date=today)

        # Prepare data to send in response
        data = {
            'clock_in': attendance.clock_in.strftime('%H:%M') if attendance.clock_in else None,
            'clock_out': attendance.clock_out.strftime('%H:%M') if attendance.clock_out else None,
            'early_exit': attendance.early_exit,  # Optionally include early_exit if you want to
        }

    except Attendance.DoesNotExist:
        # If no attendance exists for today, return None for both clock_in and clock_out
        data = {
            'clock_in': None,
            'clock_out': None,
            'early_exit': None,  # Again, optional based on your needs
        }

    return JsonResponse(data)



@login_required
def attendance_edit(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk)

    if request.method == 'POST':
        form = EmployeeAttendanceForm(request.POST, instance=attendance)
        if form.is_valid():
            form.save()
            return redirect('attendance_list')
    else:
        form = EmployeeAttendanceForm(instance=attendance)

    return render(request, 'attendance_management/attendance_edit_form.html', {
        'form': form,
        'attendance': attendance
    })

from django.shortcuts import render, redirect
from .forms import EmployeeAttendanceForm
from .models import Attendance
from employee_management.models import Employee
import datetime
from datetime import date

def employee_attendance_create(request):
    employee_id = request.COOKIES.get('employee_id')
    if not employee_id:
        return redirect('employee_login')

    employee = Employee.objects.filter(id=employee_id).first()
    if not employee:
        return redirect('employee_login')

    today = date.today()

    # Try to get today's attendance
    try:
        instance = Attendance.objects.get(employee=employee, date=today)
    except Attendance.DoesNotExist:
        instance = None

    if request.method == 'POST':
        form = EmployeeAttendanceForm(request.POST, instance=instance, employee=employee)
        print("POST Data:", request.POST)

        if form.is_valid():
            form.save()
            return redirect('employee_attendance_list')
        else:
            print("Form errors:", form.errors)
    else:
        form = EmployeeAttendanceForm(instance=instance, employee=employee)

    return render(request, 'attendance_management/employee_attendance_form.html', {
        'form': form,
        'employee': employee
    })


# Ensure the attendance view handles both clock-in and clock-out fields properly.
from datetime import datetime, time
import calendar
from django.shortcuts import render, redirect
from django.db.models.functions import ExtractYear
from calendar import monthrange
from .models import Employee, Attendance


def employee_attendance_list(request):
    # Fetch the employee ID from cookies
    employee_id = request.COOKIES.get('employee_id')
    if not employee_id:
        return redirect('employee_login')

    employee = Employee.objects.filter(id=employee_id).first()
    if not employee:
        return redirect('employee_login')

    # Get the current date and time
    now_dt = datetime.now()  # Corrected: use datetime.now() directly
    selected_month = int(request.GET.get('month', now_dt.month))
    selected_year = int(request.GET.get('year', now_dt.year))

    # Get attendance records based on selected month and year
    attendance_qs = Attendance.objects.filter(
        employee_id=employee_id,
        date__month=selected_month,
        date__year=selected_year
    )

    # Mapping attendance records by date
    attendance_map = {}
    LATE_THRESHOLD = time(9, 30)  # after 9:30 AM is considered late

    # Iterate over attendance records and determine status
    for rec in attendance_qs:
        if hasattr(rec, 'leave') and rec.leave:
            status = "Leave"
        elif hasattr(rec, 'holiday') and rec.holiday:
            status = "Holiday"
        elif rec.date.weekday() == 6:
            status = "Weekend"
        elif rec.clock_in:
            status = "Late" if rec.clock_in > LATE_THRESHOLD else "Present"
        else:
            status = "Absent"

        attendance_map[rec.date.day] = {
            'status': status,
            'clock_in': rec.clock_in,
            'clock_out': rec.clock_out
        }

    # Get first weekday and number of days in the selected month
    first_weekday, num_days = monthrange(selected_year, selected_month)
    calendar_grid = []
    week = []

    # Fill the first week with None if the month doesn't start on Monday
    for _ in range(first_weekday):
        week.append(None)

    # Generate calendar grid based on attendance data
    for day in range(1, num_days + 1):
        dt = datetime(selected_year, selected_month, day)
        rec = attendance_map.get(day)
        
        if rec:
            cell = {
                'day': day,
                'status': rec['status'],
                'clock_in': rec.get('clock_in'),
                'clock_out': rec.get('clock_out')
            }
        else:
            if dt.date().weekday() == 6:
                cell = {'day': day, 'status': 'Weekend', 'clock_in': None, 'clock_out': None}
            elif dt.date() <= now_dt.date():
                cell = {'day': day, 'status': 'Absent', 'clock_in': None, 'clock_out': None}
            else:
                cell = {'day': day, 'status': None, 'clock_in': None, 'clock_out': None}

        week.append(cell)

        if len(week) == 7:
            calendar_grid.append(week)
            week = []

    # If the last week is incomplete, fill it with None
    if week:
        while len(week) < 7:
            week.append(None)
        calendar_grid.append(week)

    # Get the list of months
    months = [{'num': i, 'name': calendar.month_name[i]} for i in range(1, 13)]

    # Get list of years available in the database for the employee
    year_qs = Attendance.objects.filter(employee_id=employee_id).annotate(
        year=ExtractYear('date')
    ).values_list('year', flat=True).distinct()

    # Sort years from the database and prepare a list of years
    years_from_db = sorted({int(y) for y in year_qs if y}, reverse=True)
    if not years_from_db:
        years_from_db = [now_dt.year]
    if now_dt.year not in years_from_db:
        years_from_db.insert(0, now_dt.year)

    for y in range(now_dt.year - 1, now_dt.year - 3, -1):
        if y not in years_from_db:
            years_from_db.append(y)

    year_list = sorted(set(years_from_db), reverse=True)
    
    # Weekdays for the header row
    weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    context = {
        'calendar_grid': calendar_grid,
        'months': months,
        'year_list': year_list,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'employee': employee,
        'weekdays': weekdays,
    }

    return render(request, 'attendance_management/employee_attendance_success.html', context)


from django.http import JsonResponse
from datetime import date  # Correct import for date
from .models import Attendance

def get_today_attendance(request):
    employee_id = request.GET.get('employee_id')
    today = date.today()  # Correct usage of date.today()

    try:
        # Try to get the attendance record for the employee on the current date
        attendance = Attendance.objects.get(employee_id=employee_id, date=today)
        
        # Format the clock-in and clock-out time if they exist
        data = {
            'clock_in': attendance.clock_in.strftime('%H:%M') if attendance.clock_in else '',
            'clock_out': attendance.clock_out.strftime('%H:%M') if attendance.clock_out else '',
        }
    except Attendance.DoesNotExist:
        # If no attendance record is found, return empty values
        data = {'clock_in': '', 'clock_out': ''}

    # Return the data as a JsonResponse
    return JsonResponse(data)



