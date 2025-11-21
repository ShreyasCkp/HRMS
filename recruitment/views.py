# recruitment/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import JobRequisitionForm


def create_requisition(request):
    if request.method == "POST":
        form = JobRequisitionForm(request.POST)
        if form.is_valid():
            requisition = form.save(commit=False)
            # any auto fields like created_by can be set here:
            # requisition.created_by = request.user
            requisition.save()
            return redirect("my_requisitions")
    else:
        form = JobRequisitionForm()

    return render(request, "recruitment/requisition_form.html", {"form": form})

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from .models import JobRequisition
from masters.models import UserCustom
from django.utils import timezone

# Helper to fetch approver
def _get_approver(request):
    username = request.session.get("username") or request.COOKIES.get("username")
    if username:
        try:
            return UserCustom.objects.get(username=username)
        except UserCustom.DoesNotExist:
            return None
    return None



def my_requisitions(request):
    """Display all job requisitions"""
    requisitions = JobRequisition.objects.all().order_by("-created_at")
    return render(request, "recruitment/my_requisitions.html", {"requisitions": requisitions})



def update_status(request, pk, status):
    requisition = get_object_or_404(JobRequisition, pk=pk)

    if request.method == "POST":
        if status.lower() == "approved":
            approver = _get_approver(request) or (request.user if request.user.is_authenticated else None)

            if hasattr(requisition, "approve"):
                requisition.approve(approver)
            else:
                requisition.status = "Approved"
                requisition.is_approved = True
                requisition.approved_by = approver
                requisition.approved_at = timezone.now()
                requisition.save()

        elif status.lower() == "rejected":
            requisition.status = "Rejected"
            requisition.is_approved = False
            requisition.approved_by = None
            requisition.approved_at = None
            requisition.save()

        # Return JSON if AJAX
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"status": requisition.status})

        return redirect("my_requisitions")

    return redirect("my_requisitions")





from django.shortcuts import render, get_object_or_404, redirect
from .models import JobRequisition, Applicant
from .forms import ApplicantForm

def job_list(request):
    jobs = JobRequisition.objects.filter(status="approved").order_by("-created_at")
    return render(request, "recruitment/job_list.html", {"jobs": jobs})

from django.contrib import messages

from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404, render
from .models import JobRequisition
from .forms import ApplicantForm

def apply_for_job(request, job_id):
    job = get_object_or_404(JobRequisition, id=job_id)

    # ✅ Check if vacancies are already filled
    if job.candidates.count() >= job.vacancies:
        messages.error(request, "Vacancies are already filled for this job.")
        return redirect("job_list")  # ✅ fixed redirect

    if request.method == "POST":
        form = ApplicantForm(request.POST, request.FILES)
        if form.is_valid():
            applicant = form.save(commit=False)
            applicant.job = job
            applicant.save()
            messages.success(request, "Application submitted successfully!")
            return redirect("job_list")  # ✅ fixed redirect
    else:
        form = ApplicantForm()

    return render(request, "recruitment/apply_for_job.html", {"form": form, "job": job}) 

def job_detail(request, job_id):
    """
    View full description of a single job requisition.
    """
    job = get_object_or_404(JobRequisition, id=job_id)
    return render(request, "recruitment/job_detail.html", {"job": job}) 

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import JobRequisition, Applicant
from .forms import ApplicantForm

# ----------------------------
# 1. View Candidate
# ----------------------------
from .forms import ApplicantForm

def view_candidate(request, applicant_id):
    applicant = get_object_or_404(Applicant, id=applicant_id)
    job = applicant.job

    # ✅ Form instance with applicant
    form = ApplicantForm(instance=applicant)

    # ✅ Disable all fields for view-only
    for field in form.fields.values():
        field.disabled = True

    return render(request, "recruitment/apply_for_job.html", {
        "form": form,
        "job": job,
        "applicant": applicant,
        "view_only": True  # template will hide submit button
    })

from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from .models import Applicant
from employee_management.models import Employee
from .forms import ApplicantForm
from django.shortcuts import get_object_or_404, redirect, render

import random, string
from django.shortcuts import render, redirect
from django.contrib import messages


def generate_employee_credentials():
    """Generate random UserID & Password (not shown in form)"""
    userid = 'EMP' + ''.join(random.choices(string.digits, k=5))
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    return userid, password


def generate_emp_code():
    """Auto-increment Employee Code in format EMP01, EMP02..."""
    last_emp = Employee.objects.all().order_by('-id').first()
    if last_emp and last_emp.emp_code:
        try:
            last_num = int(last_emp.emp_code.replace("EMP", ""))
        except ValueError:
            last_num = 0
        new_num = last_num + 1
    else:
        new_num = 1
    return f"EMP{str(new_num).zfill(2)}"

def edit_candidate(request, applicant_id):
    applicant = get_object_or_404(Applicant, id=applicant_id)
    job = applicant.job

    if request.method == "POST":
        form = ApplicantForm(request.POST, request.FILES, instance=applicant)
        if form.is_valid():
            form.save()  # Update applicant details including status

            # -------------------------------
            # ✅ Auto-create Employee if Hired
            # -------------------------------
            if applicant.status == "hired":
                # Check if Employee already exists
                if not Employee.objects.filter(email=applicant.email).exists():
                    # Generate Employee code, UserID, Password
                    emp_code = generate_emp_code()
                    userid, password = generate_employee_credentials()

                    # Create Employee object
                    employee = Employee.objects.create(
                        name=applicant.name,
                        email=applicant.email,
                        phone=applicant.phone,
                        location=applicant.location,
                        contact=applicant.phone,
                        emp_code=emp_code,
                        employee_userid=userid,
                        employee_password=password,
                        password_changed=False,
                        passcode_set=False,
                        # Map any other matching fields here
                    )

                    messages.success(
                        request,
                        f"Candidate '{applicant.name}' marked as hired and Employee created! "
                        f"Code: {emp_code}, UserID: {userid}, Password: {password}"
                    )
                else:
                    messages.info(request, f"Employee record already exists for '{applicant.name}'.")

            else:
                messages.success(request, f"Candidate '{applicant.name}' updated successfully!")

            return redirect("job_detail", job_id=job.id)
    else:
        form = ApplicantForm(instance=applicant)  # Load status field

    return render(request, "recruitment/apply_for_job.html", {
        "form": form,
        "job": job,
        "applicant": applicant
    })



# ----------------------------
# 3. Delete Candidate
# ----------------------------
def delete_candidate(request, applicant_id):
    """
    Delete a candidate safely and redirect to recruitment dashboard
    """
    applicant = get_object_or_404(Applicant, id=applicant_id)
    applicant_name = applicant.name  # store before deleting
    applicant.delete()
    messages.success(request, f"Candidate '{applicant_name}' has been deleted.")
    return redirect("recruitment_dashboard")  # Redirect to dashboard

from django.http import JsonResponse
from .models import JobRequisition


def toggle_active(request, job_id, is_active):
    try:
        job = JobRequisition.objects.get(id=job_id)
        job.is_active = bool(int(is_active))
        job.save()
        return JsonResponse({"success": True, "is_active": job.is_active})
    except JobRequisition.DoesNotExist:
        return JsonResponse({"success": False, "error": "Job not found"})

from django.shortcuts import redirect, get_object_or_404
from .models import JobRequisition

from django.shortcuts import get_object_or_404, redirect
from .models import JobRequisition

def share_on_linkedin(request, pk):
    # pk comes from the URL of the share button
    job = get_object_or_404(JobRequisition, pk=pk)
    
    # Build absolute URL of the job detail page
    job_url = request.build_absolute_uri(f"/recruitment/job/{job.id}/")
    
    # LinkedIn share URL
    linkedin_url = f"https://www.linkedin.com/sharing/share-offsite/?url={job_url}"
    
    return redirect(linkedin_url)



import re
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from django.contrib import messages
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.views.decorators.http import require_POST

from PyPDF2 import PdfReader  # pip install PyPDF2

from .models import ResumeSubmission, JobRequisition, Applicant


# ---------------- PDF Extraction ----------------
def _extract_text_from_pdf_fileobj(file_obj):
    """Return text extracted from a PDF file-like object using PyPDF2."""
    try:
        reader = PdfReader(file_obj)
        texts = []
        for page in reader.pages:
            page_text = page.extract_text() or ""
            texts.append(page_text)
        return "\n".join(texts)
    except Exception:
        return ""


def _extract_email_from_text(text):
    """Return first email found in text or None."""
    if not text:
        return None
    m = re.search(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[A-Za-z]{2,}", text)
    return m.group(0).strip().lower() if m else None


def _extract_name_from_text(text, email=None):
    """
    Heuristic to get candidate name:
    - Look for 'Name:' labels
    - Or look above email for a likely name
    """
    if not text:
        return None
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    # 1) Name: pattern
    for ln in lines:
        m = re.search(r"(?i)\bname[:\-]\s*(.+)$", ln)
        if m:
            return m.group(1).strip()
    # 2) Find email line and look above
    idx = None
    if email:
        for i, ln in enumerate(lines):
            if email in ln:
                idx = i
                break
    candidates = lines[:6] if idx is None else lines[max(0, idx - 4):idx]
    for ln in reversed(candidates):
        parts = ln.split()
        if 1 <= len(parts) <= 4 and all(p[0].isupper() for p in parts if p):
            return ln
    return None


import re
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.utils import timezone
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

from PyPDF2 import PdfReader

from .models import ResumeSubmission, JobRequisition, Applicant


# ---------------- PDF Helpers ----------------
def _extract_text_from_pdf_fileobj(file_obj):
    """Return text extracted from a PDF file-like object using PyPDF2."""
    try:
        reader = PdfReader(file_obj)
        texts = []
        for page in reader.pages:
            page_text = page.extract_text() or ""
            texts.append(page_text)
        return "\n".join(texts)
    except Exception:
        return ""


def _extract_email_from_text(text):
    """Return first email found in text or None."""
    if not text:
        return None
    # Remove extra spaces/newlines
    cleaned_text = " ".join(text.split())
    # Regex to catch emails like nischitha13@gmail.com
    m = re.search(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[A-Za-z]{2,}", cleaned_text)
    return m.group(0).strip().lower() if m else None


def _extract_name_from_text(text, email=None):
    """
    Heuristic to get candidate name:
    - Look for 'Name:' patterns first
    - Else look for 1-4 capitalized words near the email
    """
    if not text:
        return None
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

    # 1) Check "Name:" label
    for ln in lines:
        m = re.search(r"(?i)\bname[:\-]\s*(.+)$", ln)
        if m:
            return m.group(1).strip()

    # 2) If email known, look near it
    idx = None
    if email:
        for i, ln in enumerate(lines):
            if email in ln:
                idx = i
                break

    candidates = lines[max(0, idx - 4):idx] if idx else lines[:6]
    for ln in reversed(candidates):
        parts = ln.split()
        if 1 <= len(parts) <= 4 and all(p[0].isupper() for p in parts if p):
            return ln
    return None


from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils import timezone

# ---------------- Email Sending ----------------
def _send_job_email(job, applicant_email, from_email=None, extra_context=None):
    """
    Send HTML job details email using configured backend.
    Returns (success_bool, error_message_or_None).
    - extra_context: dict of extra variables to pass to the template (e.g., apply_link)
    """
    if not from_email:
        from_email = getattr(settings, "POSTMARK_SENDER", settings.DEFAULT_FROM_EMAIL)

    context = {"job": job}
    if extra_context:
        context.update(extra_context)  # merge extra context

    # Render email template with context
    html_content = render_to_string("recruitment/job_detail_email.html", context)
    subject = f"Job Details: {job.title}"

    email = EmailMultiAlternatives(subject, "", from_email, [applicant_email])
    email.attach_alternative(html_content, "text/html")

    try:
        email.send(fail_silently=False)
        return True, None
    except Exception as e:
        return False, str(e)


# ---------------- Main Views ----------------
def resume_list(request):
    """
    Show all resumes and extraction/email status.
    Frontend can show:
      - applicant.name if present else "Not Extracted"
      - applicant.email if present
      - "Email Sent" if email_sent_at is not None
    """
    resumes = (
        ResumeSubmission.objects
        .select_related("requisition", "employee")
        .prefetch_related("requisition__candidates")
        .order_by("-submitted_at")
    )

    resume_data = []
    for r in resumes:
        applicant = getattr(r, "applicant", None)
        resume_data.append({
            "resume": r,
            "applicant": applicant,
        })

    return render(request, "recruitment/resume_list.html", {"resume_data": resume_data})
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import ResumeSubmission, Applicant
from .views import _extract_text_from_pdf_fileobj, _extract_email_from_text, _extract_name_from_text

def extract_applicant(request, resume_id):
    """
    Extract name/email from PDF and save Applicant record.
    Called when recruiter clicks 'Extract' button.
    """
    # Fetch the ResumeSubmission object
    resume = get_object_or_404(ResumeSubmission, id=resume_id)
    job = resume.requisition

    # Check if resume file exists
    if not resume.resume:
        messages.error(request, "No resume file found.")
        return redirect("resume_list")

    try:
        # Open and read PDF file safely
        resume.resume.open("rb")
        pdf_text = _extract_text_from_pdf_fileobj(resume.resume)
    except Exception as e:
        messages.error(request, f"Error reading PDF: {str(e)}")
        return redirect("resume_list")
    finally:
        resume.resume.close()

    # Extract email
    email = _extract_email_from_text(pdf_text)
    if not email:
        messages.error(request, "Could not detect email in PDF.")
        return redirect("resume_list")

    # Extract name (optional fallback)
    name = _extract_name_from_text(pdf_text, email=email)

    # Create or update Applicant
    try:
        applicant, created = Applicant.objects.update_or_create(
            job=job,
            email=email,
            defaults={
                "name": name or "",
                "resume": resume.resume,          # Keep file reference
                "skills": "",
                "resume_submission": resume,     # link OneToOne
                "experience": 0,                 # default 0 to avoid null issues
            },
        )
    except Exception as e:
        messages.error(request, f"Error saving applicant: {str(e)}")
        return redirect("resume_list")

    messages.success(
        request,
        f"{'Created' if created else 'Updated'} applicant: {applicant.name or 'Unknown Name'} ({email})."
    )
    return redirect("resume_list")



from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import ResumeSubmission, Applicant
from .views import _extract_text_from_pdf_fileobj, _extract_email_from_text
from django.urls import reverse

@require_POST
def send_job_mail(request, resume_id):
    """
    Send job email to applicant.
    """
    resume = get_object_or_404(ResumeSubmission, id=resume_id)
    job = resume.requisition

    applicant = getattr(resume, "applicant", None)
    applicant_email = None

    if applicant and applicant.email:
        applicant_email = applicant.email
    else:
        if resume.resume:
            resume.resume.open("rb")
            pdf_text = _extract_text_from_pdf_fileobj(resume.resume)
            applicant_email = _extract_email_from_text(pdf_text)
            resume.resume.close()
        if not applicant_email:
            applicant_email = getattr(resume.employee, "email", None)

    if not applicant_email:
        messages.error(request, "No email found to send job details.")
        return redirect("resume_list")

    # Generate the dynamic apply link
    apply_link = request.build_absolute_uri(reverse("apply_for_job", args=[job.id]))

    # Send email
    success, error = _send_job_email(
        job, applicant_email, extra_context={"apply_link": apply_link}
    )

    if success:
        messages.success(request, f"Job email sent to {applicant_email}.")
        if applicant:
            applicant.email_sent_at = timezone.now()
            applicant.save()
        else:
            Applicant.objects.update_or_create(
                job=job,
                email=applicant_email,
                defaults={
                    "name": getattr(resume.employee, "name", ""),
                    "resume": resume.resume,
                    "resume_submission": resume,
                    "experience": 0,
                    "email_sent_at": timezone.now(),
                },
            )
    else:
        messages.error(request, f"Failed to send email: {error}")

    return redirect("resume_list")
