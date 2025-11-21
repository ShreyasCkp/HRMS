from django.shortcuts import render, redirect
from employee_management.models import Employee, Leave
from attendance_management.models import Attendance
from payroll_management.models import Payroll
from masters.models import OfficeEvent, RecentActivity, UserCustom, LeaveType
from datetime import date, timedelta
from django.db.models import Sum, Count
from django.contrib.auth.decorators import login_required
from notifications.models import Notification

def home_redirect(request):
    return redirect("login")

def dashboard(request):
    today = date.today()

    # KPIs
    total_employees = Employee.objects.filter(is_active=True).count()
    active_leaves = Leave.objects.filter(
        is_approved=True,
        start_date__lte=today,
        end_date__gte=today
    ).count()
    present_today = Attendance.objects.filter(date=today, clock_in__isnull=False).count()
    monthly_payroll = Payroll.objects.filter(
        status="Paid",
        month=today.strftime("%Y-%m")
    ).aggregate(total=Sum("net_salary"))["total"] or 0

    recent_activities = RecentActivity.objects.order_by("-timestamp")[:10]
    user_display_name = "Guest"
    user_id = request.session.get("user_id")
    if user_id:
        try:
            user = UserCustom.objects.get(id=user_id)
            user_display_name = user.username
        except UserCustom.DoesNotExist:
            pass

    upcoming_events = OfficeEvent.objects.filter(date__gte=today).order_by("date")[:5]

    # Attendance chart data (last 7 days)
    attendance_labels = [(today - timedelta(days=i)).strftime("%d %b") for i in range(6, -1, -1)]
    attendance_counts = [
        Attendance.objects.filter(date=today - timedelta(days=i), clock_in__isnull=False).count()
        for i in range(6, -1, -1)
    ]

    # ✅ Updated Leave chart using related LeaveType model
    leave_data = Leave.objects.filter(leave_type__isnull=False).values("leave_type__name").annotate(count=Count("id"))
    leave_labels = [item["leave_type__name"] for item in leave_data]
    leave_counts = [item["count"] for item in leave_data]

    # Notifications
    notifications = Notification.objects.order_by('-created_at')[:10]

    # Payroll Salary Ranges Chart
    salary_ranges = {"0-20k": 0, "20k-40k": 0, "40k-60k": 0, "60k-80k": 0, "80k+": 0}
    for emp in Payroll.objects.filter(status="Paid", month=today.strftime("%Y-%m")):
        salary = float(emp.net_salary)
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

    return render(request, "dashboard.html", context)
