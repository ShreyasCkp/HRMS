from django.shortcuts import render
from django.db.models import Count, Sum
from datetime import date
from .models import JobRequisition, Applicant

def recruitment_dashboard(request):
    today = date.today()

    # KPI Cards
    open_positions = JobRequisition.objects.filter(
        is_active=True
    ).exclude(status__in=["closed", "filled"]).aggregate(
        total=Sum("vacancies")
    )["total"] or 0

    total_applicants = Applicant.objects.count()

    in_progress = Applicant.objects.filter(
        status__in=["applied", "shortlisted"]
    ).count()

    hired_this_month = Applicant.objects.filter(
        status="hired",
        job__created_at__year=today.year,
        job__created_at__month=today.month
    ).count()

    # Job Requisitions with Applicant count
    requisitions = JobRequisition.objects.annotate(
        applicants_count=Count('candidates')
    ).order_by('-created_at')[:10]

    # ✅ Fetch all applicants with their related job
    applicants = Applicant.objects.select_related('job').order_by('-id')

    # Get all jobs (for filter dropdown)
    jobs = JobRequisition.objects.all()

    context = {
        'open_positions': open_positions,
        'total_applicants': total_applicants,
        'in_progress': in_progress,
        'hired_this_month': hired_this_month,
        'requisitions': requisitions,
        'applicants': applicants,  # all applicants
        'jobs': jobs,              # for dropdown filter
    }
    return render(request, 'recruitment_dashboard.html', context)
