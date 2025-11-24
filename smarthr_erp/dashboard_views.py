# smarthr_erp/dashboard_views.py

from datetime import date, timedelta
from functools import wraps

from django.shortcuts import render, redirect
from django.db import connection
from django.db.models import Sum, Count
from django.http import HttpResponse
from django.template import TemplateDoesNotExist, TemplateSyntaxError


# --------- custom decorator using your session auth ---------
def session_login_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.session.get("user_id"):
            # not logged in → go to login
            return redirect(f"/login/?next={request.path}")
        return view_func(request, *args, **kwargs)
    return _wrapped


# --------- SAFE imports (so Azure doesn’t 500 if something missing) ---------
try:
    from employee_management.models import Employee, Leave
except Exception:
    Employee = None
    Leave = None

try:
    from attendance_management.models import Attendance
except Exception:
    Attendance = None

try:
    from payroll_management.models import Payroll
except Exception:
    Payroll = None

try:
    from masters.models import OfficeEvent, RecentActivity, UserCustom, LeaveType
except Exception:
    OfficeEvent = RecentActivity = UserCustom = LeaveType = None

try:
    from notifications.models import Notification
except Exception:
    Notification = None


def home_redirect(request):
    """
    Only used if you still map '' -> home_redirect in urls.py.
    You can ignore this if root ('') points to login_view.
    """
    return redirect("login")


def _table_exists(model):
    """
    Avoid 'relation ... does not exist' errors on Azure.
    Checks if the table for this model actually exists in the DB.
    """
    if model is None:
        return False
    return model._meta.db_table in connection.introspection.table_names()


@session_login_required
def dashboard(request):
    today = date.today()

    # --------- DEFAULTS ---------
    total_employees = 0
    active_leaves = 0
    present_today = 0
    monthly_payroll = 0
    recent_activities = []
    upcoming_events = []
    notifications = []
    attendance_labels = [(today - timedelta(days=i)).strftime("%d %b") for i in range(6, -1, -1)]
    attendance_counts = [0] * 7
    leave_labels = []
    leave_counts = []
    salary_ranges = {"0-20k": 0, "20k-40k": 0, "40k-60k": 0, "60k-80k": 0, "80k+": 0}
    user_display_name = "Guest"

    try:
        # Employees
        if Employee is not None and _table_exists(Employee):
            total_employees = Employee.objects.filter(is_active=True).count()

        # Leaves
        if Leave is not None and _table_exists(Leave):
            active_leaves = Leave.objects.filter(
                is_approved=True,
                start_date__lte=today,
                end_date__gte=today,
            ).count()

        # Attendance today
        if Attendance is not None and _table_exists(Attendance):
            present_today = Attendance.objects.filter(
                date=today,
                clock_in__isnull=False,
            ).count()

        # Payroll + salary ranges
        if Payroll is not None and _table_exists(Payroll):
            monthly_payroll = (
                Payroll.objects.filter(status="Paid", month=today.strftime("%Y-%m"))
                .aggregate(total=Sum("net_salary"))["total"]
                or 0
            )

            for emp in Payroll.objects.filter(status="Paid", month=today.strftime("%Y-%m")):
                salary = float(emp.net_salary or 0)
                if salary <= 20000:
                    salary_ranges["0-20k"] += 1
                elif salary <= 40000:
                    salary_ranges["20k-40k"] += 1
                elif salary <= 60000:
                    salary_ranges["40k-60k"] += 1
                elif salary <= 80000:
                    salary_ranges["60k-80k"] += 1
                else:
                    salary_ranges["80k+"] += 1

        # Recent activity
        if RecentActivity is not None and _table_exists(RecentActivity):
            recent_activities = RecentActivity.objects.order_by("-timestamp")[:10]

        # Upcoming events
        if OfficeEvent is not None and _table_exists(OfficeEvent):
            upcoming_events = OfficeEvent.objects.filter(date__gte=today).order_by("date")[:5]

        # Notifications
        if Notification is not None and _table_exists(Notification):
            notifications = Notification.objects.order_by("-created_at")[:10]

        # Attendance chart last 7 days
        if Attendance is not None and _table_exists(Attendance):
            attendance_counts = [
                Attendance.objects.filter(
                    date=today - timedelta(days=i), clock_in__isnull=False
                ).count()
                for i in range(6, -1, -1)
            ]

        # Leave chart
        if Leave is not None and _table_exists(Leave):
            leave_data = (
                Leave.objects.filter(leave_type__isnull=False)
                .values("leave_type__name")
                .annotate(count=Count("id"))
            )
            leave_labels = [item["leave_type__name"] for item in leave_data]
            leave_counts = [item["count"] for item in leave_data]

        # Current user display name using your session user_id
        user_id = request.session.get("user_id")
        if user_id and UserCustom is not None and _table_exists(UserCustom):
            try:
                user = UserCustom.objects.get(id=user_id)
                user_display_name = user.username
            except UserCustom.DoesNotExist:
                pass

    except Exception as e:
        # Any DB/model error will be visible in browser now
        return HttpResponse(f"CRITICAL dashboard error (data layer): {e}", status=500)

    context = {
        "total_employees": total_employees,
        "active_leaves": active_leaves,
        "present_today": present_today,
        "monthly_payroll": monthly_payroll,
        "recent_activities": recent_activities,
        "upcoming_events": upcoming_events,
        "notifications": notifications,
        "user_display_name": user_display_name,
        "attendance_labels": attendance_labels,
        "attendance_counts": attendance_counts,
        "leave_labels": leave_labels,
        "leave_counts": leave_counts,
        "payroll_labels": list(salary_ranges.keys()),
        "payroll_counts": list(salary_ranges.values()),
    }

    # ---- render template, but show clear error if template is missing/broken ----
    try:
        return render(request, "dashboard.html", context)
    except TemplateDoesNotExist as e:
        return HttpResponse(f"TemplateDoesNotExist: {e}", status=500)
    except TemplateSyntaxError as e:
        return HttpResponse(f"TemplateSyntaxError in dashboard.html: {e}", status=500)
    except Exception as e:
        return HttpResponse(f"Unexpected error while rendering dashboard: {e}", status=500)
