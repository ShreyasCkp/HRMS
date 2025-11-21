from django import forms
from .models import Department, Employee

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description']

from django import forms
from .models import Employee

from django import forms
from .models import Employee

from django import forms
from .models import Employee


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        exclude = [
            'employee_password',
            'password_changed',
            'passcode',
            'passcode_set',
            'wrong_attempts',
            'is_locked',
            'emp_code',  # 🔹 exclude because it’s auto-generated
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
           
            'job_role': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
           
            'joining_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'dob': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'bank_name': forms.TextInput(attrs={'class': 'form-control'}),
            'ifsc_code': forms.TextInput(attrs={'class': 'form-control'}),
            'bank_account_number': forms.TextInput(attrs={'class': 'form-control'}),
            'branch_name': forms.TextInput(attrs={'class': 'form-control'}),
            'uan_number': forms.TextInput(attrs={'class': 'form-control'}),
            'pan_number': forms.TextInput(attrs={'class': 'form-control'}),
            'aadhaar_number': forms.TextInput(attrs={'class': 'form-control'}),
            'pf_number': forms.TextInput(attrs={'class': 'form-control'}),
            'esi_number': forms.TextInput(attrs={'class': 'form-control'}),
            'contact': forms.TextInput(attrs={'class': 'form-control'}),
            
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, readonly=False, **kwargs):
        super().__init__(*args, **kwargs)
        if readonly:  # make all fields readonly
            for field in self.fields.values():
                field.widget.attrs['readonly'] = True
                field.widget.attrs['disabled'] = True


# employee_management/forms.py

from django import forms
from .models import Leave

class LeaveForm(forms.ModelForm):
    class Meta:
        model = Leave
        fields = [
            "leave_type",          # ✅ ForeignKey field
            "start_date",
            "end_date",
            "reason",
            "leave_days",
            "next_working_day",
        ]
        widgets = {
            "leave_type": forms.Select(attrs={"class": "form-select"}),  # ✅ Dropdown for LeaveType
            "start_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "end_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "reason": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "leave_days": forms.NumberInput(attrs={"class": "form-control", "readonly": "readonly"}),
            "next_working_day": forms.DateInput(attrs={"class": "form-control", "type": "date", "readonly": "readonly"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["leave_type"].label = "Leave Type"
        self.fields["leave_type"].empty_label = "-- Select Leave Type --"




