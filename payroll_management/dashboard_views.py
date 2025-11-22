# payroll_management/dashboard_views.py

from datetime import date

from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Avg
from django.shortcuts import render

from .models import Payroll


@login_required
def payroll_dashboard(request):
    """
    Simple, safe payroll dashboard for the current month.
    Works the same on SQLite and Postgres.
    """
    today = date.today()
    current_month = today.strftime("%m")  # '01', '02', ...
    current_year = today.strftime("%Y")   # '2025'

    # If month is stored as 'YYYY-MM' in a CharField
    month_key = f"{current_year}-{current_month}"

    # This will work for CharField(month)
    payrolls = Payroll.objects.filter(month=month_key)

    total_processed = payrolls.filter(status="Paid").count()
    total_pending = payrolls.filter(status="Unpaid").count()
    pending_amount = (
        payrolls.filter(status="Unpaid").aggregate(total=Sum("net_salary"))["total"]
        or 0
    )
    avg_salary = payrolls.aggregate(avg=Avg("net_salary"))["avg"] or 0

    # ✅ Total Payroll (sum of net salaries for this month)
    total_payroll = payrolls.aggregate(total=Sum("net_salary"))["total"] or 0

    deduction_breakdown = {
        "income_tax": payrolls.aggregate(total=Sum("income_tax"))["total"] or 0,
        # placeholders if you add those fields later
        "health_insurance": 0,
        "retirement_fund": 0,
        "social_security": 0,
        "other": 0,
    }

    context = {
        "payrolls": payrolls,
        "total_processed": total_processed,
        "total_pending": total_pending,
        "pending_amount": pending_amount,
        "avg_salary": avg_salary,
        "total_payroll": total_payroll,
        "deduction_breakdown": deduction_breakdown,
        "month_name": today.strftime("%B %Y"),  # "November 2025"
    }
    return render(request, "payroll_dashboard.html", context)
