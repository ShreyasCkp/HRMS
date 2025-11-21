from django import forms
from .models import Payroll
from decimal import Decimal, ROUND_HALF_UP

class PayrollForm(forms.ModelForm):
    class Meta:
        model = Payroll
        fields = [
            'employee', 'month', 'basic_salary', 'hra', 'special_allowance', 'arrears',
            'pf_contribution', 'professional_tax', 'lwf_contribution', 'income_tax',
            'days_paid', 'lwop_days', 'lwop_amount', 'lwd', 'status',
            'total_payments', 'total_deductions', 'net_salary'  # ✅ Added here
        ]
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'month': forms.DateInput(attrs={'type': 'month', 'class': 'form-control'}),
            'basic_salary': forms.NumberInput(attrs={'class': 'form-control'}),
            'hra': forms.NumberInput(attrs={'class': 'form-control'}),
            'special_allowance': forms.NumberInput(attrs={'class': 'form-control'}),
            'arrears': forms.NumberInput(attrs={'class': 'form-control'}),
            'pf_contribution': forms.NumberInput(attrs={'class': 'form-control'}),
            'professional_tax': forms.NumberInput(attrs={'class': 'form-control'}),
            'lwf_contribution': forms.NumberInput(attrs={'class': 'form-control'}),
            'income_tax': forms.NumberInput(attrs={'class': 'form-control'}),
            'days_paid': forms.NumberInput(attrs={'class': 'form-control'}),
            'lwop_days': forms.NumberInput(attrs={'class': 'form-control'}),
            'lwop_amount': forms.NumberInput(attrs={'id': 'id_lwop_amount', 'class': 'form-control', 'readonly': False}),
            'total_payments': forms.NumberInput(attrs={'id': 'id_total_payments', 'class': 'form-control', 'readonly': True}),
            'total_deductions': forms.NumberInput(attrs={'id': 'id_total_deductions', 'class': 'form-control', 'readonly': True}),
            'net_salary': forms.NumberInput(attrs={'id': 'id_net_salary', 'class': 'form-control', 'readonly': True}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'lwd': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()

        def to_decimal(val):
            return Decimal(str(val or 0)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        basic = to_decimal(cleaned_data.get('basic_salary'))
        hra = to_decimal(cleaned_data.get('hra'))
        special = to_decimal(cleaned_data.get('special_allowance'))
        arrears = to_decimal(cleaned_data.get('arrears'))

        pf = to_decimal(cleaned_data.get('pf_contribution'))
        pt = to_decimal(cleaned_data.get('professional_tax'))
        lwf = to_decimal(cleaned_data.get('lwf_contribution'))
        it = to_decimal(cleaned_data.get('income_tax'))
        lwop_days = to_decimal(cleaned_data.get('lwop_days'))

        lwop_amount = (basic / Decimal('30')) * lwop_days
        lwop_amount = lwop_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        total_payments = (basic + hra + special + arrears).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        total_deductions = (pf + pt + lwf + it + lwop_amount).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        net_salary = (total_payments - total_deductions).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        cleaned_data['lwop_amount'] = lwop_amount
        cleaned_data['total_payments'] = total_payments
        cleaned_data['total_deductions'] = total_deductions
        cleaned_data['net_salary'] = net_salary

        return cleaned_data

    def save(self, commit=True):
        payroll = super().save(commit=False)

        # Assign calculated fields
        for field in ['lwop_amount', 'total_payments', 'total_deductions', 'net_salary']:
            setattr(payroll, field, self.cleaned_data.get(field))

        if commit:
            payroll.save()

        return payroll
