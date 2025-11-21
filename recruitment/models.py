from django.db import models
from masters.models import Department, JobRole, InterviewRound

class JobPosting(models.Model):
    title = models.CharField(max_length=200)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    job_role = models.ForeignKey(JobRole, on_delete=models.SET_NULL, null=True)
    description = models.TextField()
    posted_on = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

class Candidate(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    resume = models.FileField(upload_to='resumes/')
    applied_for = models.ForeignKey(JobPosting, on_delete=models.CASCADE)
    applied_on = models.DateField(auto_now_add=True)

class Interview(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    round = models.ForeignKey(InterviewRound, on_delete=models.SET_NULL, null=True)
    scheduled_on = models.DateTimeField()
    rating = models.IntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True)



# recruitment/models.py
from django.db import models
from django.utils import timezone
from masters.models import UserCustom   # <-- your custom user model
from employee_management.models import Department as EmpDepartment  # alias to be safe


# recruitment/models.py
from django.db import models
from django.utils import timezone
from django.db.models import Max
from masters.models import UserCustom
from employee_management.models import Department as EmpDepartment

class JobRequisition(models.Model):
    # ---- Choices ----
    EMPLOYMENT_TYPE_CHOICES = [
        ('full_time', 'Full-time'),
        ('part_time', 'Part-time'),
        ('contract', 'Contract'),
        ('intern', 'Internship'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('posted', 'Posted'),
        ('on_hold', 'On Hold'),
        ('rejected', 'Rejected'),
        ('filled', 'Filled'),
    ]

    # ---- Public Job Details ----
    job_id = models.CharField(
        max_length=10,
        unique=True,
        editable=False,
        help_text="Auto-generated ID like 0001"
    )
    WORK_MODE_CHOICES = [
    ('onsite', 'Onsite'),
    ('hybrid', 'Hybrid'),
    ('remote', 'Remote / Work from Home'),
    ('flexible', 'Flexible / Offset'),
]
    title = models.CharField(max_length=200)
    department = models.ForeignKey(EmpDepartment, on_delete=models.SET_NULL, null=True, blank=True)
    location = models.CharField(max_length=100, blank=True)
    vacancies = models.PositiveIntegerField(default=1)
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES, default='full_time')

    experience_min = models.PositiveIntegerField(null=True, blank=True, help_text="Years")
    experience_max = models.PositiveIntegerField(null=True, blank=True, help_text="Years")

    salary_min = models.PositiveIntegerField(null=True, blank=True, help_text="Annual INR")
    salary_max = models.PositiveIntegerField(null=True, blank=True, help_text="Annual INR")

    overview = models.TextField(blank=True, help_text="Short description or reason for hire")
    responsibilities = models.TextField(blank=True)
    required_skills = models.TextField(blank=True)
    work_mode = models.CharField(
        max_length=20,
        choices=WORK_MODE_CHOICES,
        default='onsite',
        help_text="Select the work mode: Onsite, Hybrid, Remote, or Flexible"
    )

    # ✅ NEW: Compensation & Benefits
    compensation_benefits = models.TextField(
        blank=True,
        help_text="Describe perks: health insurance, bonuses, PF, ESOPs, etc."
    )

    # ---- Internal Workflow ----
    hiring_manager = models.ForeignKey(UserCustom, on_delete=models.SET_NULL, null=True, blank=True)
    hr_email = models.EmailField(null=True, blank=True)  # NEW FIELD
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    posted_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        # Auto-generate sequential job_id like 0001
        if not self.job_id:
            max_id = JobRequisition.objects.aggregate(max_job_id=Max('id'))['max_job_id'] or 0
            self.job_id = f"{max_id + 1:04d}"


            if self.status in ['draft', 'inactive', 'active']:
             self.status = 'active' if self.is_active else 'inactive'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.job_id} - {self.title}"



# recruitment/models.py
from django.db import models
from employee_management.models import Employee

class ResumeSubmission(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    requisition = models.ForeignKey(JobRequisition, on_delete=models.CASCADE)
    resume = models.FileField(upload_to="resumes/")
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.name} → {self.requisition.title}"




from django.db import models
from .models import JobRequisition

class Applicant(models.Model):
    job = models.ForeignKey(JobRequisition, on_delete=models.CASCADE, related_name="candidates")


    resume_submission = models.OneToOneField(
        ResumeSubmission,
        on_delete=models.CASCADE,
        related_name="applicant",
        null=True,
        blank=True
    )
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    gender = models.CharField(
        max_length=10,
        choices=[("male", "Male"), ("female", "Female"), ("other", "Other")],
        blank=True, null=True
    )
    location = models.CharField(max_length=200, blank=True, null=True)
    skills = models.TextField(blank=True, null=True, help_text="Comma separated skills (e.g., Python, Django, React)")
    resume = models.FileField(upload_to="resumes/")
    experience = models.DecimalField(
    max_digits=4,
    decimal_places=1,
    help_text="Years of experience",
    null=True,
    blank=True
) 
    # ✅ Extra fields
    linkedin_url = models.URLField(blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)
    cover_letter = models.TextField(blank=True, null=True)
    current_ctc = models.CharField(max_length=50, blank=True, null=True)
    expected_ctc = models.CharField(max_length=50, blank=True, null=True)
    notice_period = models.CharField(max_length=50, blank=True, null=True)


    email_sent_at = models.DateTimeField(blank=True, null=True)


    status = models.CharField(
        max_length=20,
        choices=[
            ("applied", "Applied"),
            ("shortlisted", "Shortlisted"),
            ("rejected", "Rejected"),
            ("selected", "Selected"),
            ("hired", "Hired"),

        ],
        default="applied",
    )

    def mark_email_sent(self):
        """Helper function to mark email as sent with current timestamp"""
        self.email_sent_at = timezone.now()
        self.save(update_fields=["email_sent_at"])

        
    def __str__(self):
        return f"{self.name} - {self.job.title}"




