from django.urls import path
from .dashboard_views import recruitment_dashboard
from django.http import HttpResponse 
from . import views

def export_recruitment(request):
    import csv
    from django.http import HttpResponse
    from .models import JobPosting, Candidate
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="recruitment_export.csv"'
    writer = csv.writer(response)
    writer.writerow(['Job Title', 'Department', 'Job Role', 'Description', 'Posted On', 'Is Active'])
    for job in JobPosting.objects.all():
        writer.writerow([
            job.title,
            job.department.name if job.department else '',
            job.job_role.name if job.job_role else '',
            job.description,
            job.posted_on,
            job.is_active
        ])
    writer.writerow([])
    writer.writerow(['Candidate Name', 'Email', 'Phone', 'Applied For', 'Applied On'])
    for cand in Candidate.objects.all():
        writer.writerow([
            cand.name,
            cand.email,
            cand.phone,
            cand.applied_for.title if cand.applied_for else '',
            cand.applied_on
        ])
    return response

def post_job(request):
    from .forms import JobPostingForm
    from django.shortcuts import render, redirect
    if request.method == 'POST':
        form = JobPostingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('recruitment_dashboard')
    else:
        form = JobPostingForm()
    return render(request, 'recruitment/post_job_form.html', {'form': form})

urlpatterns = [
    path('dashboard/', recruitment_dashboard, name='recruitment_dashboard'),
    path('export/', export_recruitment, name='recruitment_export'),
    path('post_job/', post_job, name='post_job'),


    path("requisitions/create/", views.create_requisition, name="create_requisition"),
   path("recruitment/requisitions/", views.my_requisitions, name="my_requisitions"),

    path("requisitions/<int:pk>/<str:status>/", views.update_status, name="update_status"),




    path("jobs/", views.job_list, name="job_list"),   # careers page
    path('job/<int:job_id>/apply/', views.apply_for_job, name='apply_for_job'),


     path('candidate/<int:applicant_id>/view/', views.view_candidate, name='view_candidate'),
    path('candidate/<int:applicant_id>/edit/', views.edit_candidate, name='edit_candidate'),
    path('candidate/<int:applicant_id>/delete/', views.delete_candidate, name='delete_candidate'),

    path('job/<int:job_id>/', views.job_detail, name='job_detail'),


    path('recruitment/toggle-active/<int:job_id>/<int:is_active>/', views.toggle_active, name='toggle_active'),

   path('recruitment/job/<int:pk>/share/', views.share_on_linkedin, name='share_on_linkedin'),


    path('resumes/', views.resume_list, name='resume_list'),  # Global resume list
    path("send-job-mail/<int:resume_id>/", views.send_job_mail, name="send_job_mail"),
    path(
        "resumes/extract/<int:resume_id>/",
        views.extract_applicant,
        name="extract_applicant"
    ),
]
