from django.db import models
from django.contrib.auth.models import User

class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
from django.db import models
from django.contrib.auth.models import User
from masters.models import JobRole


class Employee(models.Model):

    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)

    # 🔹 Auto increment employee code like EMP01, EMP02
    emp_code = models.CharField(max_length=20, blank=True, null=True, unique=True)

    name = models.CharField(max_length=100, blank=True, null=True)
    designation = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    uan_number = models.CharField(max_length=20, blank=True, null=True)
    pan_number = models.CharField(max_length=20, blank=True, null=True)
    aadhaar_number = models.CharField(max_length=20, blank=True, null=True)
    pf_number = models.CharField(max_length=20, blank=True, null=True)
    esi_number = models.CharField(max_length=20, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    joining_date = models.DateField(blank=True, null=True)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    ifsc_code = models.CharField(max_length=20, blank=True, null=True)
    bank_account_number = models.CharField(max_length=30, blank=True, null=True)
    job_role = models.ForeignKey(JobRole, on_delete=models.SET_NULL, null=True, blank=True)

    contact = models.CharField(max_length=20, blank=True, null=True)
    photo = models.ImageField(upload_to='employee_photos/', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    # 🔹 Login-related fields
    employee_userid = models.CharField(max_length=50, unique=True, blank=True, null=True)
    employee_password = models.CharField(max_length=50, blank=True, null=True)  # plain text password
    password_changed = models.BooleanField(default=False)
    passcode = models.CharField(max_length=10, blank=True, null=True)
    passcode_set = models.BooleanField(default=False)
    wrong_attempts = models.IntegerField(default=0)
    is_locked = models.BooleanField(default=False)

    
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=10, blank=True, null=True)
   
    branch_name = models.CharField(max_length=100, blank=True, null=True)

    def save(self, *args, **kwargs):
        # Auto-generate emp_code if not already set
        if not self.emp_code:
            last_emp = Employee.objects.all().order_by("-id").first()
            if last_emp and last_emp.emp_code:
                try:
                    last_number = int(last_emp.emp_code.replace("EMP", ""))
                except ValueError:
                    last_number = 0
                new_number = last_number + 1
            else:
                new_number = 1

            self.emp_code = f"EMP{str(new_number).zfill(2)}"  # EMP01, EMP02, ...

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name or self.user} ({self.department})"



class Onboarding(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE)
    start_date = models.DateField()
    completed = models.BooleanField(default=False)

class Offboarding(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE)
    end_date = models.DateField()
    completed = models.BooleanField(default=False)


from datetime import timedelta
from django.db import models
from masters.models import LeaveType
from employee_management.models import Employee  # adjust import if needed

class Leave(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="leaves")

    # 🔁 Updated from CharField to ForeignKey
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE, null=True, blank=True)

    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField(blank=True)
    admin_reason = models.TextField(blank=True, null=True)

    # Auto-calculated fields
    leave_days = models.PositiveIntegerField(default=0)
    next_working_day = models.DateField(null=True, blank=True)

    approved_by = models.CharField(max_length=150, null=True, blank=True)
    is_approved = models.BooleanField(null=True, blank=True, default=None)
    applied_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "employee_management_leave"
        ordering = ["-applied_on"]

    def __str__(self):
        # ✅ Safe fallback to avoid crashes if leave_type is missing
        leave_type_name = self.leave_type.name if self.leave_type else "Unknown Leave Type"
        return f"{self.employee.name} - {leave_type_name} ({self.leave_days} days)"

    def save(self, *args, **kwargs):
        # ✅ Calculate total leave days
        if self.start_date and self.end_date:
            self.leave_days = (self.end_date - self.start_date).days + 1

        # ✅ Calculate next working day (skip weekends)
        if self.end_date:
            next_day = self.end_date + timedelta(days=1)
            while next_day.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
                next_day += timedelta(days=1)
            self.next_working_day = next_day

        super().save(*args, **kwargs)



from django.db import models
from django.utils import timezone

class Notification(models.Model):
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return self.message

