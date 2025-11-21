from django.shortcuts import render
from django.db.models import Sum, Avg
from .models import Payroll
from datetime import date
from django.contrib.auth.decorators import login_required

def payroll_dashboard(request):
    today = date.today()
    current_month = today.strftime('%m')
    current_year = today.strftime('%Y')

    # Filter payrolls for current month
    payrolls = Payroll.objects.filter(month__startswith=f"{current_year}-{current_month}")

    total_processed = payrolls.filter(status='Paid').count()
    total_pending = payrolls.filter(status='Unpaid').count()
    pending_amount = payrolls.filter(status='Unpaid').aggregate(total=Sum('net_salary'))['total'] or 0
    avg_salary = payrolls.aggregate(avg=Avg('net_salary'))['avg'] or 0

    # ✅ Total Payroll (sum of net salaries for this month)
    total_payroll = payrolls.aggregate(total=Sum('net_salary'))['total'] or 0

    deduction_breakdown = {
        'income_tax': payrolls.aggregate(total=Sum('income_tax'))['total'] or 0,
        'health_insurance': 0,
        'retirement_fund': 0,
        'social_security': 0,
        'other': 0,
    }

    return render(request, 'payroll_dashboard.html', {
        'payrolls': payrolls,
        'total_processed': total_processed,
        'total_pending': total_pending,
        'pending_amount': pending_amount,
        'avg_salary': avg_salary,
        'total_payroll': total_payroll,  # ✅ Add to context
        'deduction_breakdown': deduction_breakdown,
        'month_name': today.strftime('%B %Y'),
    })
