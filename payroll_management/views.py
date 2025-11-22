from django.shortcuts import render, redirect, get_object_or_404
from django.http import (
    HttpResponse,
    FileResponse,
    HttpResponseForbidden,
    JsonResponse,
)
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.db import IntegrityError
from django.db.models import Sum, Avg
from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from django.contrib.staticfiles.storage import staticfiles_storage

from decimal import Decimal
import calendar
import num2words

from .models import Payroll
from .forms import PayrollForm
from .utils import generate_payslip_pdf
from employee_management.models import Employee


def payroll_list(request):
    payrolls = Payroll.objects.select_related('employee').all()

    # ✅ Total unpaid amount
    unpaid_amount = Payroll.objects.filter(status='Unpaid').aggregate(total=Sum('net_salary'))['total'] or 0

    # ✅ Average salary across all payrolls
    avg_salary = payrolls.aggregate(avg=Avg('net_salary'))['avg'] or 0

    context = {
        'payrolls': payrolls,
        'unpaid_amount': unpaid_amount,
        'avg_salary': avg_salary,
    }
    return render(request, 'payroll_management/payroll_list.html', context)



from django.shortcuts import render, redirect
from .models import Payroll
from .forms import PayrollForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError

from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from .forms import PayrollForm


def payroll_create(request):
    if request.method == 'POST':
        form = PayrollForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # use form.save(commit=False) so you can ensure any fields are explicitly set
                payroll = form.save(commit=False)

                # ensure critical fields are set (form.clean already computes these, but keep safe)
                payroll.employee = form.cleaned_data.get('employee')
                payroll.lwd = form.cleaned_data.get('lwd')

                # If you want to double-calc lwop_amount here (optional):
                lwop_days = form.cleaned_data.get('lwop_days') or 0
                basic_salary = form.cleaned_data.get('basic_salary') or 0
                payroll.lwop_amount = (basic_salary / 30) * lwop_days

                # totals (clean() already provides these, but assign again)
                payroll.total_payments = form.cleaned_data.get('total_payments')
                payroll.total_deductions = form.cleaned_data.get('total_deductions')
                payroll.net_salary = form.cleaned_data.get('net_salary')

                payroll.save()
                messages.success(request, 'Payroll saved successfully.')

                # If user clicked "Generate PDF" you can detect it:
                if 'generate' in request.POST:
                    # implement your own PDF generation/redirect here
                    return redirect('payroll_list')  # or generate PDF
                return redirect('payroll_list')

            except IntegrityError:
                messages.error(request, 'You have already created a payroll for this employee for the selected month.')
            except Exception as e:
                # Surface unexpected errors to console + UI (for dev)
                print("Unexpected payroll save error:", e)
                messages.error(request, f'Unexpected error saving payroll: {e}')
        else:
            # show errors (they will also appear next to fields because form is passed back)
            print("Form errors:", form.errors)   # check runserver console
            messages.error(request, 'You have already created a payroll for this employee for the selected month.')
    else:
        form = PayrollForm()

    return render(request, 'payroll_management/payroll_form.html', {'form': form})





def export_payroll(request):
    import csv
    from django.http import HttpResponse
    from .models import Payroll
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="payroll_export.csv"'
    writer = csv.writer(response)
    writer.writerow(['Employee', 'Month', 'Basic Salary', 'Tax', 'Deductions', 'Net Salary', 'Status'])
    for payroll in Payroll.objects.all():
        writer.writerow([
            str(payroll.employee),
            payroll.month,
            payroll.basic_salary,
            payroll.tax,
            payroll.deductions,
            payroll.net_salary,
            payroll.status
        ])
    return response



def process_payroll(request):
    from .models import Payroll
    from datetime import date
    from django.shortcuts import redirect
    month = date.today().strftime('%Y-%m')
    Payroll.objects.filter(month=month, status='Unpaid').update(status='Paid')
    return redirect('payroll_list')


def tax_calculations(request):
    return HttpResponse('Payroll tax calculations coming soon.')




from calendar import month_abbr
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseForbidden
from .models import Payroll
import calendar


def payroll_view(request, pk):
    payroll = get_object_or_404(Payroll, pk=pk)

    # 🚫 Prevent access if unauthorized
    if hasattr(payroll.employee, 'user') and request.user != payroll.employee.user and not request.user.is_staff:
        return HttpResponseForbidden("You are not authorized to view this payslip.")

    # ✅ Format month as "Jan-2025"
    try:
        year, month = str(payroll.month).split('-')
        formatted_month_year = f"{calendar.month_abbr[int(month)]}-{year}"
    except (ValueError, AttributeError, IndexError):
        formatted_month_year = "Invalid-Date"

    # ✅ Add images for view mode too
    signature_image_url = request.build_absolute_uri(
        staticfiles_storage.url("images/signature_refined.png")
    )
    company_logo_url = request.build_absolute_uri(
        staticfiles_storage.url("images/logo.png")
    )

    return render(request, 'payroll_management/payslip_template.html', {
        'payroll': payroll,
        'formatted_month_year': formatted_month_year,
        'signature_image_url': signature_image_url,
        'company_logo_url': company_logo_url,
    })



def payroll_edit(request, pk):
    payroll = get_object_or_404(Payroll, pk=pk)
    if request.method == 'POST':
        form = PayrollForm(request.POST, request.FILES, instance=payroll)
        if form.is_valid():
            payroll = form.save(commit=False)

            total_payments = (
                payroll.basic_salary +
                payroll.hra +
                payroll.special_allowance +
                payroll.arrears
            )
            total_deductions = (
                payroll.pf_contribution +
                payroll.professional_tax +
                payroll.lwf_contribution +
                payroll.income_tax +
                payroll.lwop_amount
            )
            payroll.total_payments = total_payments
            payroll.total_deductions = total_deductions
            payroll.net_salary = total_payments - total_deductions

            payroll.save()
            messages.success(request, 'Payroll record updated!')
            return redirect('payroll_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PayrollForm(instance=payroll)

    return render(request, 'payroll_management/payroll_form.html', {'form': form})




def payroll_records(request):
    status = request.GET.get('status')
    if status:
        payrolls = Payroll.objects.filter(status=status)
    else:
        payrolls = Payroll.objects.all()
    return render(request, 'payroll_list.html', {'payrolls': payrolls})


from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, FileResponse
from django.contrib.auth.models import AnonymousUser
from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.conf import settings
import os
from io import BytesIO
from .models import Payroll
from django.contrib.staticfiles.storage import staticfiles_storage
from decimal import Decimal
import num2words
import calendar

def generate_payslip_download(request, pk):
    """
    ✅ Single endpoint:
       - Always generates the payslip if not generated already.
       - If ?action=download and user is HR/Admin/owner → downloads PDF.
    """
    payroll = get_object_or_404(Payroll, pk=pk)

    # Always generate if not generated already
    if not payroll.payslip_pdf:
        # Convert net salary to words
        net_salary = Decimal(payroll.net_salary or 0)
        rupees = int(net_salary)
        paise = int((net_salary - rupees) * 100)

        if paise > 0:
            net_salary_in_words = (
                num2words.num2words(rupees, lang="en_IN").title()
                + " Rupees And "
                + num2words.num2words(paise, lang="en_IN").title()
                + " Paise Only"
            )
        else:
            net_salary_in_words = (
                num2words.num2words(rupees, lang="en_IN").title()
                + " Rupees Only"
            )

        # Format month (e.g., Jan-2025)
        try:
            if isinstance(payroll.month, str) and "-" in payroll.month:
                year, month = payroll.month.split("-")
                formatted_month_year = f"{calendar.month_abbr[int(month)]}-{year}"
            else:
                formatted_month_year = "Invalid-Date"
        except Exception:
            formatted_month_year = "Invalid-Date"

        # ✅ Absolute static image URLs
        signature_image_url = request.build_absolute_uri(
            staticfiles_storage.url("images/signature_refined.png")
        )
        company_logo_url = request.build_absolute_uri(
            staticfiles_storage.url("images/logo.png")
        )

        # Context for template
        context = {
            "payroll": payroll,
            "formatted_month_year": formatted_month_year,
            "net_salary_in_words": net_salary_in_words,
            "signature_image_url": signature_image_url,
            "company_logo_url": company_logo_url,
        }

        # ✅ Generate PDF using helper (xhtml2pdf inside)
        pdf_bytes = generate_payslip_pdf(
            "payroll_management/payslip_template.html",
            context,
        )

        if not pdf_bytes:
            return HttpResponse("Error generating PDF", status=500)

        filename = f"payslip_{payroll.employee.id}_{payroll.month}.pdf"
        payroll.payslip_pdf.save(filename, ContentFile(pdf_bytes), save=True)

    # ------------------------------------------------------------
    # ✅ Download flow
    # ------------------------------------------------------------
    action = request.GET.get("action", "").lower()
    user = request.user
    employee_user = getattr(payroll.employee, "user", None)

    if action == "download" and not isinstance(user, AnonymousUser):
        is_hr_or_admin = user.is_staff
        is_employee_owner = (employee_user == user)

        if is_hr_or_admin or is_employee_owner:
            file_path = payroll.payslip_pdf.path
            if os.path.exists(file_path):
                return FileResponse(
                    payroll.payslip_pdf.open("rb"),
                    as_attachment=True,
                    filename=os.path.basename(file_path),
                )
            else:
                return HttpResponse("Payslip not found.", status=404)
        else:
            return HttpResponse("Unauthorized", status=403)

    # Default response (just generated, redirect back)
    messages.success(request, "Payslip generated successfully.")
    return redirect(request.META.get("HTTP_REFERER", "payroll_list"))






from django.http import JsonResponse
from employee_management.models import Employee  # Adjust import if needed

def get_employee_data(request):
    emp_id = request.GET.get('employee_id')
    data = {}

    if emp_id:
        try:
            emp = Employee.objects.get(id=emp_id)
            data = {
                'emp_code': emp.emp_code,
                'name': emp.name,
                'designation': emp.designation,
                'department': emp.department.name if emp.department else '',
            }
        except Employee.DoesNotExist:
            data = {'error': 'Employee not found'}

    return JsonResponse(data)

