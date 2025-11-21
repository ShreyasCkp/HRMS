from django.db import models
from employee_management.models import Employee
import calendar
from num2words import num2words
from decimal import Decimal, ROUND_HALF_UP

class Payroll(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    month = models.CharField(max_length=7)  # Format: YYYY-MM

    basic_salary = models.DecimalField(max_digits=14, decimal_places=2)
    hra = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    special_allowance = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    arrears = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    pf_contribution = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    professional_tax = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    lwf_contribution = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    income_tax = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    total_payments = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_deductions = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    net_salary = models.DecimalField(max_digits=14, decimal_places=2)

    lwop_amount = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True, default=0)
    days_paid = models.PositiveIntegerField(default=0)
    lwop_days = models.PositiveIntegerField(default=0)

    status = models.CharField(max_length=10, choices=[('Paid', 'Paid'), ('Unpaid', 'Unpaid')], default='Unpaid')
    payslip_pdf = models.FileField(upload_to='payslips/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    lwd = models.DateField(null=True, blank=True, verbose_name="Last Working Day")

    class Meta:
        unique_together = ('employee', 'month')

    def __str__(self):
        return f"{self.employee} - {self.month} ({self.status})"

    def round_amount(self, value, digits=2):
        """Helper to round to 2 or 3 decimal places"""
        if value is None:
            return Decimal("0.00")
        fmt = "0.00" if digits == 2 else "0.000"
        return Decimal(value).quantize(Decimal(fmt), rounding=ROUND_HALF_UP)

    @property
    def year(self):
        try:
            return int(self.month.split('-')[0])
        except:
            return 0

    @property
    def month_number(self):
        try:
            return int(self.month.split('-')[1])
        except:
            return 0

    @property
    def days_in_month(self):
        try:
            return calendar.monthrange(self.year, self.month_number)[1]
        except:
            return 0

    @property
    def net_pay_in_words(self):
        try:
            return num2words(self.net_salary, to='currency', lang='en_IN').replace('euro', 'rupees')
        except Exception:
            return str(self.net_salary)

    @property
    def formatted_month_year(self):
        try:
            from calendar import month_abbr
            return f"{month_abbr[self.month_number]}-{self.year}"
        except Exception:
            return "Invalid-Date"
