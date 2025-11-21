from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date
from employee_management.models import Leave
from masters.models import OfficeEvent


# 🔹 Helper to fetch approver name from session/cookie
def _get_approver_name(request):
    return request.session.get("username") or request.COOKIES.get("username") or ""



def leave_dashboard(request):
    # KPI counts
    total_requests = Leave.objects.count()
    pending_requests = Leave.objects.filter(is_approved__isnull=True).count()
    approved_requests = Leave.objects.filter(is_approved=True).count()
    rejected_requests = Leave.objects.filter(is_approved=False).count()

    # Latest leave requests
    leave_requests = Leave.objects.select_related("employee").order_by("-applied_on")[:20]

    # Upcoming events
    upcoming_events = OfficeEvent.objects.filter(date__gte=date.today()).order_by("date")[:5]

    return render(request, "leave_dashboard.html", {
        "total_requests": total_requests,
        "pending_requests": pending_requests,
        "approved_requests": approved_requests,
        "rejected_requests": rejected_requests,
        "leave_requests": leave_requests,
        "upcoming_events": upcoming_events,
    })


# 🔹 Approve leave

def leave_approve(request, leave_id):
    leave = get_object_or_404(Leave, id=leave_id)

    if request.method == "POST":
        leave.is_approved = True
        leave.approved_by = _get_approver_name(request)
        leave.admin_reason = request.POST.get("admin_reason", "")
        leave.save()

        messages.success(request, f"Leave approved for {leave.employee.name}.")
        return redirect("leave_dashboard")

    return redirect("leave_dashboard")


# 🔹 Reject leave

def leave_reject(request, leave_id):
    leave = get_object_or_404(Leave, id=leave_id)

    if request.method == "POST":
        leave.is_approved = False
        leave.approved_by = _get_approver_name(request)
        leave.admin_reason = request.POST.get("admin_reason", "")
        leave.save()

        messages.error(request, f"Leave rejected for {leave.employee.name}.")
        return redirect("leave_dashboard")

    return redirect("leave_dashboard")
