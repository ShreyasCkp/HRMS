# smarthr_erp/dashboard_views.py

from datetime import date

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

# We import inside try/except so that if any app/migration is missing,
# the dashboard still doesn't crash.
try:
    from attendance_management.models import Attendance
except Exception:
    Attendance = None

try:
    from employee_management.models import Employee
except Exception:
    Employee = None

try:
    from leave_management.models import Leave
except Exception:
    Leave = None

try:
    from payroll_management.models import Payroll
except Exception:
    Payroll = None


@login_required
def home_redirect(request):
    """
    When someone hits '/', send them to the main dashboard.
    """
    return redirect("dashboard")


@login_required
def dashboard(request):
    """
    Global HR dashboard.

    This version is **defensive**:
    - Any DB / model / migration error is caught.
    - The dashboard will still render with zeros instead of crashing with 500.
    """

    today = date.today()

    # Defaults (if anything goes wrong, we keep these)
    total_employees = 0
    total_payroll_records = 0
    todays_attendance = 0
    pending_leaves = 0
    paid_payroll = 0
    unpaid_payroll = 0

    # ---- Employees ----
    try:
        if Employee is not None:
            total_employees = Employee.objects.count()
    except Exception as e:
        print("Dashboard error: Employee count failed:", e)

    # ---- Payroll ----
    try:
        if Payroll is not None:
            total_payroll_records = Payroll.objects.count()
            paid_payroll = Payroll.objects.filter(status="Paid").count()
            unpaid_payroll = Payroll.objects.filter(status="Unpaid").count()
    except Exception as e:
        print("Dashboard error: Payroll queries failed:", e)

    # ---- Attendance (for today) ----
    try:
        if Attendance is not None:
            # Adjust field name if your model uses something else (e.g., 'attendance_date')
            todays_attendance = Attendance.objects.filter(date=today).count()
    except Exception as e:
        print("Dashboard error: Attendance query failed:", e)

    # ---- Pending leaves ----
    try:
        if Leave is not None:
            # Adjust status value if you use something else (e.g., 'P', 'Pending Approval', etc.)
            pending_leaves = Leave.objects.filter(status="Pending").count()
    except Exception as e:
        print("Dashboard error: Leave query failed:", e)

    context = {
        "today": today,
        "total_employees": total_employees,
        "total_payroll_records": total_payroll_records,
        "todays_attendance": todays_attendance,
        "pending_leaves": pending_leaves,
        "paid_payroll": paid_payroll,
        "unpaid_payroll": unpaid_payroll,
    }

    return render(request, "dashboard.html", context)
