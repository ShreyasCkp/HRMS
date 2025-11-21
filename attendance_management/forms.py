from django import forms
from .models import Attendance
from employee_management.models import Employee
import datetime
from django.core.exceptions import ValidationError

class AttendanceForm(forms.ModelForm):
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.all(),
        empty_label="Select Employee",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'employee_select'})
    )

    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'readonly': 'readonly', 'class': 'form-control'}),
        initial=datetime.date.today
    )

    clock_in = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control', 'readonly': 'readonly', 'id': 'clock_in_time'}),
        initial=datetime.datetime.now().time()
    )

    clock_out = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control', 'id': 'clock_out_time'})
    )

    early_exit = forms.BooleanField(
        required=False,
        label="Early Exit",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = Attendance
        fields = ['employee', 'date', 'clock_in', 'clock_out', 'early_exit']

    def __init__(self, *args, **kwargs):
        employee = kwargs.pop('employee', None)
        super().__init__(*args, **kwargs)

        if employee:
            self.fields['employee'].initial = employee

    # Strip seconds and microseconds before saving
    def clean_clock_in(self):
        clock_in = self.cleaned_data.get('clock_in')
        if clock_in:
            return clock_in.replace(second=0, microsecond=0)  # Remove seconds and microseconds
        return clock_in

    def clean_clock_out(self):
        clock_out = self.cleaned_data.get('clock_out')
        if clock_out:
            return clock_out.replace(second=0, microsecond=0)  # Remove seconds and microseconds
        return clock_out

    def clean(self):
        cleaned_data = super().clean()
        clock_in = cleaned_data.get('clock_in')
        clock_out = cleaned_data.get('clock_out')

        # Check if clock-out is after clock-in
        if clock_in and clock_out and clock_out < clock_in:
            raise ValidationError("Clock-out time must be after clock-in time.")

        return cleaned_data










from django import forms
from .models import Attendance
import datetime
from django.forms.widgets import DateInput, TimeInput

class EmployeeAttendanceForm(forms.ModelForm):
    date = forms.DateField(
        widget=DateInput(attrs={
            'type': 'date',
            'readonly': 'readonly',
            'class': 'form-control'
        }),
        initial=datetime.date.today
    )

    class Meta:
        model = Attendance
        fields = ['employee', 'date', 'clock_in', 'clock_out', 'early_exit']
        widgets = {
            'clock_in': TimeInput(attrs={
                'type': 'time',
                'class': 'form-control',
            }),
            'clock_out': TimeInput(attrs={
                'type': 'time',
                'class': 'form-control',
            }),
            'early_exit': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        employee = kwargs.pop('employee', None)
        super().__init__(*args, **kwargs)
        self.fields['employee'].widget = forms.HiddenInput()
        if employee:
            self.fields['employee'].initial = employee

    def clean(self):
        cleaned_data = super().clean()
        clock_in = cleaned_data.get('clock_in')
        clock_out = cleaned_data.get('clock_out')

        if clock_in and clock_out and clock_out < clock_in:
            raise forms.ValidationError("Clock-out must be after clock-in.")
        return cleaned_data
