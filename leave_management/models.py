from django.db import models
from employee_management.models import Employee

class LeaveType(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    default_balance = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class LeaveRequest(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=[('Pending','Pending'),('Approved','Approved'),('Rejected','Rejected')], default='Pending')
    applied_on = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_leaves')

    def __str__(self):
        return f"{self.employee} - {self.leave_type} ({self.status})"

class LeaveBalance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    balance = models.IntegerField(default=0)

    class Meta:
        unique_together = ('employee', 'leave_type')
