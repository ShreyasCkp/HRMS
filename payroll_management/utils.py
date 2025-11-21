from xhtml2pdf import pisa
from io import BytesIO
from django.template.loader import render_to_string


def generate_payslip_pdf(payroll):
    html = render_to_string('payroll_management/payslip_template.html', {'payroll': payroll})
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode('utf-8')), result)
    if not pdf.err:
        return result.getvalue()
    return None