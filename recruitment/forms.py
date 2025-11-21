from django import forms
from .models import JobPosting, Interview


class JobPostingForm(forms.ModelForm):
    class Meta:
        model = JobPosting
        fields = ['title', 'department', 'job_role', 'description', 'is_active']
        # If you add a user-editable date field, add a widget here

class InterviewForm(forms.ModelForm):
    class Meta:
        model = Interview
        fields = ['candidate', 'round', 'scheduled_on', 'rating', 'feedback']
        widgets = {
            'scheduled_on': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
from django import forms
from .models import JobRequisition
from masters.models import UserCustom
from employee_management.models import Department as EmpDepartment  # Correct department model


class JobRequisitionForm(forms.ModelForm):
    class Meta:
        model = JobRequisition
        fields = [
            'title', 'department', 'hiring_manager', 'vacancies',
            'location', 'employment_type', 'experience_min', 'experience_max',
            'salary_min', 'salary_max', 'work_mode', 'hr_email','overview',
            'responsibilities', 'required_skills',
            'compensation_benefits', 'is_active',
        ]
        widgets = {
            'overview': forms.Textarea(attrs={'rows': 3}),
            'responsibilities': forms.Textarea(attrs={'rows': 3}),
            'required_skills': forms.Textarea(attrs={'rows': 2}),
            'compensation_benefits': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ✅ Only pull departments from employee_management_department
        self.fields['department'].queryset = EmpDepartment.objects.all()

        # ✅ Hiring managers from UserCustom
        self.fields['hiring_manager'].queryset = UserCustom.objects.all()


from django import forms
from .models import Applicant

class ApplicantForm(forms.ModelForm):
    class Meta:
        model = Applicant
        fields = [
            "name", "email", "phone", "gender", "location", "skills",
            "resume", "experience", "linkedin_url", "github_url",
            "cover_letter", "current_ctc", "expected_ctc", "notice_period","status",
        ]
        widgets = {
            "cover_letter": forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
            "skills": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ✅ Make status optional for apply
        self.fields["status"].required = False       
