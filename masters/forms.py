from django import forms
from .models import Department, JobRole, LeaveType, PerformanceKPI, InterviewRound

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description']

class JobRoleForm(forms.ModelForm):
    class Meta:
        model = JobRole
        fields = ['name', 'description']

class LeaveTypeForm(forms.ModelForm):
    class Meta:
        model = LeaveType
        fields = ['name', 'description', 'default_balance']

from django import forms
from .models import PerformanceKPI

class PerformanceKPIForm(forms.ModelForm):
    class Meta:
        model = PerformanceKPI
        fields = ['name', 'description', 'max_score', 'goal_threshold', 'review_frequency_days']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'max_score': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'goal_threshold': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'review_frequency_days': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }

class InterviewRoundForm(forms.ModelForm):
    class Meta:
        model = InterviewRound
        fields = ['name', 'description']

from django import forms
from .models import UserCustom
import re

class UserAddForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        help_text="Start with a capital letter, include lowercase, one special character, and one number. Length 8–16."
    )

    class Meta:
        model = UserCustom
        fields = ["username", "password", "is_locked"]

    def clean_password(self):
        password = self.cleaned_data.get("password", "")
        pattern = r"^[A-Z][a-z]+(?=.*[0-9])(?=.*[!@#$%^&*])[A-Za-z0-9!@#$%^&*]{7,15}$"
        if not re.match(pattern, password):
            raise forms.ValidationError(
                "Password must start with a capital letter, include lowercase, one special character, one number, and be 8–16 characters."
            )
        return password


class UserEditForm(forms.ModelForm):
    password = forms.CharField(
        required=False,   # ✅ Optional in edit mode
        widget=forms.PasswordInput,
        help_text="Leave blank to keep existing password."
    )

    class Meta:
        model = UserCustom
        fields = ["username",  "password", "is_locked"]

    def clean_password(self):
        password = self.cleaned_data.get("password", "")
        if password:  # Validate only if user entered a new one
            pattern = r"^[A-Z][a-z]+(?=.*[0-9])(?=.*[!@#$%^&*])[A-Za-z0-9!@#$%^&*]{7,15}$"
            if not re.match(pattern, password):
                raise forms.ValidationError(
                    "Password must start with a capital letter, include lowercase, one special character, one number, and be 8–16 characters."
                )
        return password
