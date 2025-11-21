from django.shortcuts import render, redirect, get_object_or_404
from .models import Department, Employee
from .forms import DepartmentForm, EmployeeForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def department_list(request):
    departments = Department.objects.all()
    return render(request, 'employee_management/department_list.html', {'departments': departments})


def department_create(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Department created successfully!')
            return redirect('department_list')
    else:
        form = DepartmentForm()
    return render(request, 'employee_management/department_form.html', {'form': form})


def employee_list(request):
    employees = Employee.objects.select_related('user', 'department').all()
    return render(request, 'employee_management/employee_list.html', {'employees': employees})


import random, string
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import EmployeeForm
from .models import Employee


import random
import string
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import EmployeeForm
from .models import Employee

import logging

logger = logging.getLogger(__name__)

def generate_employee_credentials():
    """Generate random UserID & Password (ensure UserID is unique)"""
    
    def generate_unique_userid():
        attempt = 0
        while True:
            # Generate a random user ID (e.g., "EMP1001", "EMP1002", ...)
            userid = 'EMP' + ''.join(random.choices(string.digits, k=5))
            attempt += 1
            logger.debug(f"Attempt #{attempt}: Generated user ID: {userid}")

            # Ensure the generated ID is not conflicting with existing ones.
            if not Employee.objects.filter(employee_userid=userid).exists():
                return userid
            # If the user ID already exists, regenerate it.

    def generate_password():
        # Generate a random password (for example, 8 characters long with letters and digits)
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        return password

    # Generate the unique employee user ID and password
    userid = generate_unique_userid()
    password = generate_password()

    return userid, password



# Function to generate auto-incrementing employee code
def generate_emp_code():
    """Auto-increment Employee Code in format EMP01, EMP02..."""
    last_emp = Employee.objects.all().order_by('-id').first()  # Get the last created employee

    if last_emp and last_emp.emp_code:  # If there's an existing employee
        try:
            last_num = int(last_emp.emp_code.replace("EMP", ""))
        except ValueError:
            last_num = 0  # Default to 0 if there’s an error parsing the code
        new_num = last_num + 1
    else:
        new_num = 1  # Start from EMP01 if no employees exist

    return f"EMP{str(new_num).zfill(2)}"  # Format the code as EMP01, EMP02, etc.


# Employee create view
def employee_create(request):
    # Generate the employee code and unique user ID and password
    emp_code = generate_emp_code()
    userid, password = generate_employee_credentials()

    if request.method == 'POST':
        emp_form = EmployeeForm(request.POST, request.FILES)

        if emp_form.is_valid():
            # Check if the user ID already exists in the database
            if Employee.objects.filter(employee_userid=userid).exists():
                # Regenerate if the user ID exists
                userid, password = generate_employee_credentials()

            # Save the employee with the generated user_id and password
            employee = emp_form.save(commit=False)
            employee.emp_code = emp_code
            employee.employee_userid = userid
            employee.employee_password = password
            employee.password_changed = False
            employee.passcode_set = False
            employee.save()

            messages.success(
                request,
                f"Employee created successfully! "
                f"Code: {emp_code}, UserID: {userid}, Password: {password}"
            )
            return redirect('employee_dashboard')
    else:
        emp_form = EmployeeForm()

    # Define the sections for the form
    employment_fields = ['employee_userid', 'department', 'designation', 'job_role', 'location', 'joining_date', 'experience']
    personal_fields = ['dob', 'email', 'phone', 'pan_number', 'aadhaar_number', 'contact']
    compliance_fields = ['uan_number', 'pf_number', 'esi_number']
    bank_fields = ['bank_name', 'ifsc_code', 'bank_account_number', 'branch_name']

    return render(request, 'employee_management/employee_form.html', {
        'emp_form': emp_form,
        'generated_empcode': emp_code,
        'form_title': 'Add',
        'is_edit': False,
        'is_view': False,
        'employment_fields': employment_fields,
        'personal_fields': personal_fields,
        'compliance_fields': compliance_fields,
        'bank_fields': bank_fields,
    })






def employee_view(request, pk):
    """Show employee details (readonly mode)."""
    employee = get_object_or_404(Employee, pk=pk)
    emp_form = EmployeeForm(instance=employee)

    # mark all fields as readonly/disabled
    for field in emp_form.fields.values():
        field.widget.attrs['readonly'] = True
        field.widget.attrs['disabled'] = True   # works for dropdowns/select

    return render(request, 'employee_management/employee_form.html', {
        'emp_form': emp_form,
        'generated_empcode': employee.emp_code,
        'is_view': True,   # 👈 flag for template
    })




def employee_edit(request, pk):
    """Edit employee details."""
    employee = get_object_or_404(Employee, pk=pk)

    if request.method == 'POST':
        emp_form = EmployeeForm(request.POST, request.FILES, instance=employee)
        if emp_form.is_valid():
            emp_form.save()
            messages.success(request, f"Employee {employee.emp_code} updated successfully!")
            return redirect('employee_list')
    else:
        emp_form = EmployeeForm(instance=employee)

    return render(request, 'employee_management/employee_form.html', {
        'emp_form': emp_form,
        'generated_empcode': employee.emp_code,
        'edit_mode': True,
    })



def employee_delete(request, pk):
    """Delete employee immediately without confirmation page."""
    employee = get_object_or_404(Employee, pk=pk)
    emp_code = employee.emp_code
    employee.delete()
    messages.success(request, f"Employee {emp_code} deleted successfully!")
    return redirect('employee_dashboard')






from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Employee  # adjust app name

def redirect_to_login(request):
    return redirect('employee_login_view')


from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Employee


def employee_login_view(request):
    context = {}

    if request.method == 'POST' and 'password' in request.POST:
        employee_userid = request.POST.get('employee_userid', '').strip()
        password = request.POST.get('password', '').strip()
        context['selected_user'] = employee_userid

        try:
            employee = Employee.objects.get(employee_userid=employee_userid)

            if employee.is_locked:
                context['error'] = "Account is locked. Contact admin."
                return render(request, 'employee_management/employee_login.html', context)

            if employee.employee_password != password:
                employee.wrong_attempts = (employee.wrong_attempts or 0) + 1
                if employee.wrong_attempts >= 3:
                    employee.is_locked = True
                employee.save()
                context['error'] = "Invalid password."
                return render(request, 'employee_management/employee_login.html', context)

            # ✅ Successful login
            employee.wrong_attempts = 0
            employee.save()

            # ---- FIX: Save to session ----
            request.session["employee_id"] = employee.id
            request.session["employee_userid"] = employee.employee_userid
            request.session["employee_name"] = employee.name or ""

            # optional cookies (if you need them)
            response = HttpResponseRedirect(
                reverse('employee_set_passcode') if not employee.passcode_set else reverse('employee_dashboard_view')
            )
            response.set_cookie('employee_id', employee.id)
            response.set_cookie('employee_userid', employee.employee_userid)
            response.set_cookie('employee_name', employee.name or "")
            return response

        except Employee.DoesNotExist:
            context['error'] = "Invalid credentials."

    return render(request, 'employee_management/employee_login.html', context)



def employee_set_passcode(request):
    employee_userid = request.COOKIES.get('employee_userid')
    if not employee_userid:
        return redirect('employee_login_view')

    employee = get_object_or_404(Employee, employee_userid=employee_userid)
    error = None

    if request.method == 'POST':
        passcode = request.POST.get('passcode', '').strip()
        confirm_passcode = request.POST.get('confirm_passcode', '').strip()

        if passcode != confirm_passcode:
            error = "Passcodes do not match."
        elif not passcode.isdigit() or len(passcode) != 4:
            error = "Passcode must be exactly 4 digits."
        else:
            employee.passcode = passcode
            employee.passcode_set = True
            employee.save()
            return redirect('employee_dashboard_view')

    return render(request, 'employee_management/employee_set_passcode.html', {
        'error': error,
        'employee_userid': employee_userid
    })



def employee_password_reset_view(request):
    """
    Flow:
    1. Show userID + passcode screen
    2. If passcode OK → show new password screen
    3. Reset password and redirect to login
    """
    context = {}
    employee_userid = request.GET.get('employee_userid', '').strip() or request.POST.get('employee_userid', '').strip()
    context['selected_user'] = employee_userid

    # Step 1: verify passcode
    if request.method == 'POST' and 'verify_passcode' in request.POST:
        passcode = request.POST.get('passcode', '').strip()
        try:
            employee = Employee.objects.get(employee_userid=employee_userid)
            if str(employee.passcode) == passcode:
                context['reset'] = True
                context['passcode_verified'] = True
            else:
                context['reset'] = True
                context['error'] = "Invalid passcode."
        except Employee.DoesNotExist:
            context['reset'] = True
            context['error'] = "User not found."
        return render(request, 'employee_management/employee_login.html', context)

    # Step 2: reset password
    if request.method == 'POST' and 'password_reset_submit' in request.POST:
        new_password = request.POST.get('new_password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        try:
            employee = Employee.objects.get(employee_userid=employee_userid)
            if new_password != confirm_password:
                context['reset'] = True
                context['passcode_verified'] = True
                context['error'] = "Passwords do not match."
            else:
                employee.employee_password = new_password  # plain text reset
                employee.wrong_attempts = 0
                employee.is_locked = False
                employee.save()
                context['success_message'] = "Password reset successful. Please login."
        except Employee.DoesNotExist:
            context['reset'] = True
            context['error'] = "User ID not found."

        return render(request, 'employee_management/employee_login.html', context)

    # Initial screen (step 1)
    context['reset'] = True
    return render(request, 'employee_management/employee_login.html', context)


def employee_logout(request):
    response = redirect('employee_login_view')
    response.delete_cookie('employee_id')
    response.delete_cookie('employee_userid')
    response.delete_cookie('employee_name')
    return response


def employee_dashboard_view(request):
    employee_userid = request.COOKIES.get('employee_userid')
    if not employee_userid:
        return redirect('employee_login_view')
    return render(request, 'employee_management/employee_dashboard1.html')

from datetime import timedelta, date
import calendar
from django.shortcuts import render, redirect, get_object_or_404
from attendance_management.models import Attendance
from payroll_management.models import Payroll
from .models import Leave
from employee_management.models import Employee, LeaveType
from django.db.models import Sum

def employee_dashboard_view2(request):
    employee_id = request.session.get("employee_id")
    if not employee_id:
        return redirect("employee_login_view")
 
    employee = get_object_or_404(Employee, pk=employee_id)
    today = date.today()
 
    # 1. Total leaves taken (only Approved and ended on or before today)
    total_leaves_taken = Leave.objects.filter(
        employee=employee,
        is_approved=True,
        end_date__lte=today
    ).aggregate(Sum('leave_days'))['leave_days__sum'] or 0
 
    # 2. Attendance today
    try:
        att = Attendance.objects.get(employee=employee, date=today)
        is_present_today = bool(att.clock_in)
    except Attendance.DoesNotExist:
        is_present_today = False
 
    # 3. Attendance percentage till today, ignoring Sundays
    current_year = today.year
    current_month = today.month
    first_day = date(current_year, current_month, 1)
    days_to_check = (today - first_day).days + 1
 
    total_working_days = 0
    present_days = 0
    for i in range(days_to_check):
        d = first_day + timedelta(days=i)
        if d.weekday() == 6:  # Sunday skip
            continue
        total_working_days += 1
        try:
            a = Attendance.objects.get(employee=employee, date=d)
            if a.clock_in:
                present_days += 1
        except Attendance.DoesNotExist:
            pass
 
    attendance_percentage = round((present_days / total_working_days) * 100, 2) if total_working_days > 0 else 0
 
    # 4. Leaves overlapping the current month (all statuses)
    first_of_month = first_day
    last_of_month = date(current_year, current_month, calendar.monthrange(current_year, current_month)[1])
 
    leaves = Leave.objects.filter(
        employee=employee,
        start_date__lte=last_of_month,
        end_date__gte=first_of_month
    ).order_by('start_date')
 
    # 5. Next upcoming approved leave
    next_upcoming_leave = Leave.objects.filter(
        employee=employee,
        is_approved=True,
        start_date__gte=today
    ).order_by('start_date').first()
 
    # 6. Payslips
    payslips = Payroll.objects.filter(employee=employee).order_by('-month')
    payslip_count = payslips.count()
    last_payslip = payslips.first()
 
    formatted_last_month = None
    if last_payslip and last_payslip.month:
        try:
            y, m = str(last_payslip.month).split('-')
            formatted_last_month = f"{calendar.month_abbr[int(m)]}-{y}"
        except Exception:
            formatted_last_month = last_payslip.month

    # 7. Leave Balance
    leave_balance_info = {}
    leave_types = LeaveType.objects.all()

    for leave_type in leave_types:
        # Total taken leaves for this type
        total_taken_for_type = Leave.objects.filter(
            employee=employee,
            leave_type=leave_type,
            is_approved=True
        ).aggregate(Sum('leave_days'))['leave_days__sum'] or 0

        # Calculate the pending leaves
        pending_leaves = leave_type.default_balance - total_taken_for_type

        leave_balance_info[leave_type.name] = {
            'total_taken': total_taken_for_type,
            'pending': pending_leaves,
            'balance': leave_type.default_balance
        }
 
    context = {
        "employee": employee,
        "total_leaves_taken": total_leaves_taken,
        "is_present_today": is_present_today,
        "attendance_percentage": attendance_percentage,
        "leaves": leaves,
        "upcoming_leave": next_upcoming_leave,
        "payslip_count": payslip_count,
        "last_payslip": formatted_last_month,
        "leave_balance_info": leave_balance_info
    }
 
    return render(request, 'employee_management/employee_dashboard2.html', context)


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Employee, Notification
from .forms import EmployeeForm  # Assuming you have this form for Employee model
from datetime import date
from dateutil.relativedelta import relativedelta


def employee_profile(request):
    employee_userid = request.COOKIES.get("employee_userid")
    if not employee_userid:
        return redirect("employee_login_view")

    employee = get_object_or_404(Employee, employee_userid=employee_userid)

    today = date.today()
    joining_date = employee.joining_date
    experience = None
    if joining_date:
        diff = relativedelta(today, joining_date)
        experience = f"{diff.years} years, {diff.months} months, {diff.days} days"

    bank_fields_filled = all([
        employee.bank_name,
        employee.ifsc_code,
        employee.bank_account_number
    ])

    if request.method == "POST":
        form = EmployeeForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            # Check if bank details changed
            bank_name_new = form.cleaned_data['bank_name']
            ifsc_code_new = form.cleaned_data['ifsc_code']
            bank_acc_num_new = form.cleaned_data['bank_account_number']

            bank_changed = (
                employee.bank_name != bank_name_new or
                employee.ifsc_code != ifsc_code_new or
                employee.bank_account_number != bank_acc_num_new
            )

            # Save bank details
            employee.bank_name = bank_name_new
            employee.ifsc_code = ifsc_code_new
            employee.bank_account_number = bank_acc_num_new
            employee.save()

            if bank_changed:
                # Create notification for admin/HR
                Notification.objects.create(
                    message=f"Employee {employee.name} (ID: {employee.emp_code}) has updated their bank details."
                )

            return redirect("employee_profile")
    else:
        form = EmployeeForm(instance=employee)

    # Check if 'edit_bank' query parameter is in the URL
    edit_bank = request.GET.get('edit_bank') == 'true'
    
    return render(request, "employee_management/employee_profile.html", {
        "employee": employee,
        "form": form,  # Pass the form for rendering
        "experience": experience,
        "bank_form": form if edit_bank else None,  # Show form only if edit_bank is True
        "edit_bank": edit_bank,  # Flag to show form in template
    })

from datetime import date, timedelta
import calendar
from django.shortcuts import render, get_object_or_404

from .models import Leave,Employee


from datetime import date, timedelta
import calendar
from django.shortcuts import render, get_object_or_404
from .models import Leave, Employee


def employee_calendar(request):
    employee_userid = request.COOKIES.get("employee_userid")
    employee = get_object_or_404(Employee, employee_userid=employee_userid)

    today = date.today()

    year = int(request.GET.get("year", today.year))
    month = int(request.GET.get("month", today.month))

    cal = calendar.Calendar(firstweekday=6)
    month_days = cal.monthdatescalendar(year, month)
    weekdays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

    prev_month = month - 1 or 12
    prev_year = year - 1 if month == 1 else year
    next_month = month + 1 if month < 12 else 1
    next_year = year + 1 if month == 12 else year

    leaves = Leave.objects.filter(
        employee=employee,
        start_date__lte=date(year, month, calendar.monthrange(year, month)[1]),
        end_date__gte=date(year, month, 1),
    )

    # ✅ Build leave list with explicit status
    leaves_list = []
    highlights_json = []

    for leave in leaves:
        # Determine leave status
        if leave.is_approved:
            status = "approved"
            color = "green"
        elif leave.approved_by:  # Rejected case
            status = "rejected"
            color = "red"
        else:
            status = "pending"
            color = "orange"

        # ✅ Sidebar leave entry
        leaves_list.append({
            "leave_type": leave.get_leave_type_display() if hasattr(leave, "get_leave_type_display") else leave.leave_type,
            "start_date": leave.start_date,
            "end_date": leave.end_date,
            "status": status,
            "reason": leave.reason,
        })

        # ✅ Highlight each day of the leave in calendar
        day_range = (leave.end_date - leave.start_date).days + 1
        for i in range(day_range):
            day = leave.start_date + timedelta(days=i)
            highlights_json.append({
                "date_day": day.day,
                "date_month": day.month,
                "date_year": day.year,
                "color": color,
                "title": leave.leave_type,
            })

    context = {
        "employee": employee,
        "today": today,
        "year": year,
        "month": month,
        "month_name": calendar.month_name[month],
        "month_days": month_days,
        "weekdays": weekdays,
        "prev_month": prev_month,
        "prev_year": prev_year,
        "next_month": next_month,
        "next_year": next_year,
        "highlights_json": highlights_json,
        "leaves_list": leaves_list,
    }

    return render(request, "employee_management/employee_calendar.html", context)

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.utils.safestring import mark_safe
from django.urls import reverse
from channels.layers import get_channel_layer
import json

from .models import Leave, Employee
from .forms import LeaveForm

def employee_leave_create(request, leave_id=None):
    employee_userid = request.COOKIES.get("employee_userid")
    if not employee_userid:
        return redirect("employee_login_view")

    employee = get_object_or_404(Employee, employee_userid=employee_userid)
    leave = get_object_or_404(Leave, id=leave_id, employee=employee) if leave_id else None

    full_name = employee.name or (employee.user.get_full_name() if hasattr(employee, 'user') else "Employee")

    if request.method == "POST":
        form = LeaveForm(request.POST, instance=leave)
        if form.is_valid():
            leave_obj = form.save(commit=False)
            leave_obj.employee = employee

            # Force-leave_type assignment from form
            lt = form.cleaned_data.get("leave_type")
            leave_obj.leave_type = lt

            # Optionally reset approval fields if editing
            if leave_id:
                leave_obj.is_approved = None
                leave_obj.approved_by = None
                leave_obj.admin_reason = None

            leave_obj.save()

            if leave_id:
                message_text = f"{full_name} has updated a leave request from {leave_obj.start_date} to {leave_obj.end_date}."
            else:
                message_text = f"{full_name} has applied for leave from {leave_obj.start_date} to {leave_obj.end_date}."

            # WebSocket notification (if using channels)
            try:
                channel_layer = get_channel_layer()
                if channel_layer:
                    notification_message = f'New leave request: {message_text}'
                    channel_layer.group_send(
                        "notifications_group",
                        {
                            'type': 'send_notification',
                            'message': notification_message
                        }
                    )
            except Exception as e:
                print("Error sending notification:", e)

            return JsonResponse({
                'status': 'success',
                'message': message_text,
                'redirect_url': reverse('employee_calendar')
            })
    else:
        form = LeaveForm(instance=leave)

    leaves = Leave.objects.filter(employee=employee).select_related("leave_type").order_by("-applied_on")
    existing_leaves = list(leaves.values("start_date", "end_date", "leave_type", "id", "is_approved"))
    existing_leaves_json = mark_safe(json.dumps(existing_leaves, default=str))

    return render(
        request,
        "employee_management/employee_leave_form.html",
        {
            "form": form,
            "leaves": leaves,
            "existing_leaves": existing_leaves_json,
            "edit_leave": leave,
            "title": "Leave Form",
        },
    )



def check_existing_leave(employee, new_leave):
    """
    Check if the new leave request exceeds the allowed balance for the leave type or if it conflicts with existing leave.
    Returns True if no conflict, False if conflict exists.
    """
    # Check if there are any existing leaves for this employee and leave type
    leaves = Leave.objects.filter(employee=employee, leave_type=new_leave.leave_type)

    # Calculate the total leave days taken for the selected leave type
    total_taken_leaves = sum(leave.leave_days for leave in leaves)

    # Check if the total taken leaves exceeds the allowed balance for the leave type
    if total_taken_leaves + new_leave.leave_days > new_leave.leave_type.default_balance:
        return False  # Conflict detected: employee has exceeded the allowed balance

    # Check for overlapping leave requests
    for leave in leaves:
        if (new_leave.start_date <= leave.end_date and new_leave.end_date >= leave.start_date):
            return False  # Conflict detected: leave dates overlap

    return True


from masters.models import LeaveType
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def check_leave_balance(request, leave_type_id):
    try:
        leave_type = LeaveType.objects.get(id=leave_type_id)
        employee_userid = request.COOKIES.get("employee_userid")
        employee = Employee.objects.get(employee_userid=employee_userid)

        # Get all leaves taken for the given leave type by the employee
        leaves_taken = Leave.objects.filter(employee=employee, leave_type=leave_type)
        total_leaves_taken = sum(leave.leave_days for leave in leaves_taken)

        # Check if the total leaves taken exceed the allowed balance
        if total_leaves_taken >= leave_type.default_balance:
            return JsonResponse({'success': False, 'message': f"You have exceeded the maximum leaves of {leave_type.default_balance} for this leave type."})
        
        return JsonResponse({'success': True})

    except LeaveType.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Invalid leave type.'})
    except Employee.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Employee not found.'})








from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Leave


# 🔹 Helper to fetch approver name from session/cookie
def _get_approver_name(request):
    """
    Returns the username of the currently logged-in user.
    Uses session first, then cookie.
    Returns empty string if no user is logged in.
    """
    return request.session.get("username") or request.COOKIES.get("username") or ""


from masters.models import LeaveType
from django.shortcuts import render
from masters.models import LeaveType
from django.shortcuts import render


def employee_leave_list(request):
    # Fetch all leave types as a dict {id: name}
    leave_type_dict = {lt.id: lt.name for lt in LeaveType.objects.all()}

    leaves = Leave.objects.select_related('leave_type', 'employee').all().order_by("-applied_on", "-start_date")

    return render(
        request,
        "employee_management/employee_leave_list.html",
        {
            "leaves": leaves,
            "leave_type_dict": leave_type_dict
        }
    )


# views.py

from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from .models import Leave
from .views import _get_approver_name

def leave_approve(request, leave_id):
    leave = get_object_or_404(Leave, id=leave_id)
    if request.method == "POST":
        approver_name = _get_approver_name(request) or "Unknown"
        leave.is_approved = True
        leave.approved_by = approver_name
        if request.content_type == 'application/json':
            import json
            data = json.loads(request.body)
            leave.admin_reason = data.get('admin_reason', '')
        leave.save()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})
        return HttpResponseRedirect(reverse('leave_dashboard'))  # Replace 'leave_list' with your actual URL name
    return JsonResponse({'status': 'error'})

def leave_reject(request, leave_id):
    leave = get_object_or_404(Leave, id=leave_id)
    if request.method == "POST":
        approver_name = _get_approver_name(request) or "Unknown"
        leave.is_approved = False
        leave.approved_by = approver_name
        if request.content_type == 'application/json':
            import json
            data = json.loads(request.body)
            leave.admin_reason = data.get('admin_reason', '')
        leave.save()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})
        return HttpResponseRedirect(reverse('leave_dashboard'))  # Replace 'leave_list' with your actual URL name
    return JsonResponse({'status': 'error'})






import json
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Avg
from employee_management.models import Employee
from performance_management.models import PerformanceReview, PerformanceScore, PerformanceKPI


def employee_performance(request):
    employee_userid = request.COOKIES.get("employee_userid")
    if not employee_userid:
        return redirect("employee_login_view")

    employee = get_object_or_404(Employee, employee_userid=employee_userid)

    reviews = PerformanceReview.objects.filter(employee=employee).prefetch_related("scores__kpi")

    quarters = ["Q1", "Q2", "Q3", "Q4"]
    quarter_scores = {}
    kpi_quarter_data = {q: {} for q in quarters}

    for q in quarters:
        qs = reviews.filter(review_period__icontains=q)
        if qs.exists():
            avg_score = PerformanceScore.objects.filter(review__in=qs).aggregate(avg=Avg("score"))["avg"]
            quarter_scores[q] = float(round(avg_score, 2)) if avg_score else 0.0

            kpis = (
                PerformanceScore.objects.filter(review__in=qs)
                .values("kpi__name")
                .annotate(avg=Avg("score"))
            )
            for k in kpis:
                kpi_quarter_data[q][k["kpi__name"]] = float(round(k["avg"], 2))
        else:
            quarter_scores[q] = 0.0

    kpis = PerformanceKPI.objects.all()
    kpi_labels = []
    kpi_actual = []
    kpi_max = []

    for k in kpis:
        avg_score = (
            PerformanceScore.objects.filter(review__in=reviews, kpi=k)
            .aggregate(avg=Avg("score"))["avg"]
        )
        kpi_labels.append(k.name)
        kpi_actual.append(float(round(avg_score, 2)) if avg_score else 0.0)
        kpi_max.append(float(k.max_score))

    return render(request, "employee_management/employee_performance.html", {
        "employee": employee,
        "reviews": reviews,
        "quarter_scores": quarter_scores,
        "kpi_quarter_data": json.dumps(kpi_quarter_data),  # ✅ safe now
        "kpi_labels": json.dumps(kpi_labels),
        "kpi_actual": json.dumps(kpi_actual),
        "kpi_max": json.dumps(kpi_max),
    })


# payroll_management/views.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from payroll_management.models import Payroll
from employee_management.models import Employee
from django.shortcuts import redirect

def employee_payslips(request):
    employee_userid = request.COOKIES.get('employee_userid')
    if not employee_userid:
        return redirect('employee_login_view')  # not logged in

    employee = get_object_or_404(Employee, employee_userid=employee_userid)
    payslips = Payroll.objects.filter(employee=employee).order_by('month')  # Ascending for graph

    # Prepare data for chart
    chart_labels = [p.formatted_month_year for p in payslips]
    net_salaries = [p.net_salary for p in payslips]

    return render(request, 'employee_management/employee_payslips.html', {
        'payslips': payslips,
        'chart_labels': chart_labels,
        'net_salaries': net_salaries,
        'employee_userid': employee_userid,  # pass it to template
    })


from django.http import HttpResponseForbidden, FileResponse, Http404
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from payroll_management.models import Payroll

from django.http import HttpResponseForbidden, FileResponse, Http404

def download_payslip(request, payslip_id):
    payslip = get_object_or_404(Payroll, id=payslip_id)

    employee_userid = request.COOKIES.get('employee_userid')
    is_employee_match = payslip.employee.employee_userid == employee_userid

    # Allow either: matched employee or Django admin
    if not is_employee_match and not request.user.is_staff:
        return HttpResponseForbidden("You are not authorized to access this payslip.")

    if not payslip.payslip_pdf:
        raise Http404("Payslip file not available.")

    return FileResponse(payslip.payslip_pdf.open('rb'), as_attachment=True)



    from django.shortcuts import render
from recruitment.models import JobRequisition
from employee_management.models import Employee

def employee_job_list(request):
    """
    Show ALL JobRequisition entries (active or inactive) to the employee
    identified by cookie employee_userid – no login required.
    """
    # 1️⃣ Get employee id from cookie
    employee_userid = request.COOKIES.get("employee_userid")

    employee = None
    if employee_userid:
        # optional: check if this employee exists
        try:
            employee = Employee.objects.get(employee_userid=employee_userid)
        except Employee.DoesNotExist:
            employee = None

    # 2️⃣ Fetch all jobs (you can further filter if needed)
    requisitions = JobRequisition.objects.all().order_by("-created_at")

    # 3️⃣ Pass to template
    return render(
        request,
        "employee_management/employee_job_list.html",
        {
            "employee": employee,          # so you can greet them
            "requisitions": requisitions,  # full job list
        }
    )


from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from recruitment.models import JobRequisition, ResumeSubmission
from employee_management.models import Employee

def upload_resume(request, requisition_id):
    requisition = get_object_or_404(JobRequisition, id=requisition_id)

    # Get employee from session
    employee_id = request.session.get("employee_id")
    employee = None
    if employee_id:
        employee = get_object_or_404(Employee, id=employee_id)

    if request.method == "POST" and employee:
        resume = request.FILES.get("resume")
        if resume:
            ResumeSubmission.objects.create(
                employee=employee,
                requisition=requisition,
                resume=resume
            )
            messages.success(request, f"Resume uploaded successfully for {requisition.title}!")
            return redirect("employee_job_list")

    return redirect("employee_job_list")
