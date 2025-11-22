# payroll_management/utils.py
from django.template.loader import get_template
from io import BytesIO

def generate_payslip_pdf(template_src, context_dict):
    # Local import to avoid crashing at startup
    from xhtml2pdf import pisa

    template = get_template(template_src)
    html = template.render(context_dict)

    result = BytesIO()
    pdf = pisa.CreatePDF(html, dest=result)

    if pdf.err:
        return None

    return result.getvalue()
