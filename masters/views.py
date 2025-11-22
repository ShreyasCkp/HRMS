from django.shortcuts import render, redirect
from .models import   JobRole, LeaveType, PerformanceKPI, InterviewRound
from .forms import  JobRoleForm, LeaveTypeForm, PerformanceKPIForm, InterviewRoundForm
from django.contrib import messages
from employee_management.models import Department as masterdepartment
from django.contrib.auth.decorators import login_required


def master_dashboard(request):
    return render(request, 'masters/master_dashboard.html')
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from employee_management.models import Department
from employee_management.forms import DepartmentForm



def department_list(request):
    """List all departments."""
    departments = Department.objects.all().order_by('name')
    return render(request, 'masters/department_list.html', {'departments': departments})



def department_create(request):
    """Create a new department."""
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Department created successfully!')
            return redirect('department_list')
        messages.error(request, '⚠️ Please correct the errors below.')
    else:
        form = DepartmentForm()
    return render(request, 'masters/department_form.html', {
        'form': form,
        'form_mode': 'create'
    })



def department_view(request, pk):
    """
    View department details in read-only mode.
    """
    dept = get_object_or_404(Department, pk=pk)
    form = DepartmentForm(instance=dept)

    # 🔒 Make fields read-only
    for field in form.fields.values():
        field.widget.attrs.update({'readonly': True, 'disabled': True})

    return render(request, 'masters/department_form.html', {
        'form': form,
        'form_mode': 'view'
    })



def department_edit(request, pk):
    """Edit an existing department."""
    dept = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=dept)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Department updated successfully!')
            return redirect('department_list')
        messages.error(request, '⚠️ Please correct the errors below.')
    else:
        form = DepartmentForm(instance=dept)
    return render(request, 'masters/department_form.html', {
        'form': form,
        'form_mode': 'edit'
    })




def department_delete(request, pk):
    """Delete a department (POST only)."""
    dept = get_object_or_404(Department, pk=pk)
    dept.delete()
    messages.success(request, '🗑️ Department deleted successfully!')
    return redirect('department_list')


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import JobRole
from .forms import JobRoleForm

def jobrole_list(request):
    jobroles = JobRole.objects.all()
    return render(request, 'masters/jobrole_list.html', {'jobroles': jobroles})

def jobrole_create(request):
    return jobrole_form_common(request)

def jobrole_edit(request, pk):
    jobrole = get_object_or_404(JobRole, pk=pk)
    return jobrole_form_common(request, instance=jobrole)

def jobrole_view(request, pk):
    """Open the same form page but in read-only mode."""
    jobrole = get_object_or_404(JobRole, pk=pk)
    form = JobRoleForm(instance=jobrole)
    return render(request, 'masters/jobrole_form.html', {
        'form': form,
        'view_mode': True   # 🔑 tells template to disable fields
    })

def jobrole_form_common(request, instance=None):
    if request.method == 'POST':
        form = JobRoleForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            msg = 'Job Role updated!' if instance else 'Job Role created!'
            messages.success(request, msg)
            return redirect('jobrole_list')
    else:
        form = JobRoleForm(instance=instance)
    return render(request, 'masters/jobrole_form.html', {'form': form})

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import JobRole

def jobrole_delete(request, pk):
    """
    Handles delete via GET (from modal link) or POST.
    """
    jobrole = get_object_or_404(JobRole, pk=pk)

    # Allow GET since modal uses an <a href> (no form/POST)
    if request.method in ['GET', 'POST']:
        jobrole.delete()
        messages.success(request, f'Job Role "{jobrole.name}" deleted successfully!')
        return redirect('jobrole_list')

    # Fallback (shouldn’t really hit here)
    messages.error(request, 'Invalid request method.')
    return redirect('jobrole_list')



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import LeaveType
from .forms import LeaveTypeForm

# List all leave types
def leavetype_list(request):
    leavetypes = LeaveType.objects.all()
    return render(request, 'masters/leavetype_list.html', {'leavetypes': leavetypes})

# Create new leave type
def leavetype_create(request):
    return leavetype_form_common(request)

# Edit leave type
def leavetype_edit(request, pk):
    leavetype = get_object_or_404(LeaveType, pk=pk)
    return leavetype_form_common(request, instance=leavetype)

# View leave type (read-only)
def leavetype_view(request, pk):
    leavetype = get_object_or_404(LeaveType, pk=pk)
    form = LeaveTypeForm(instance=leavetype)
    # Disable all fields
    for field in form.fields.values():
        field.widget.attrs['readonly'] = True
        field.widget.attrs['disabled'] = True
    return render(request, 'masters/leavetype_form.html', {
        'form': form,
        'view_mode': True
    })

# Common form handler for create & edit
def leavetype_form_common(request, instance=None):
    if request.method == 'POST':
        form = LeaveTypeForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            msg = 'Leave Type updated!' if instance else 'Leave Type created!'
            messages.success(request, msg)
            return redirect('leavetype_list')
    else:
        form = LeaveTypeForm(instance=instance)
    return render(request, 'masters/leavetype_form.html', {'form': form})

    
def leavetype_delete(request, pk):
    leavetype = get_object_or_404(LeaveType, pk=pk)
    # Only delete on POST (form submission from modal)
    if request.method == 'POST':
        leavetype.delete()
        messages.success(request, 'Leave Type deleted!')
    return redirect('leavetype_list')

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import PerformanceKPI
from .forms import PerformanceKPIForm
from decimal import Decimal



def kpi_list(request):
    kpis = PerformanceKPI.objects.all()
    return render(request, 'masters/kpi_list.html', {'kpis': kpis})






def kpi_create(request):
    if request.method == 'POST':
        form = PerformanceKPIForm(request.POST)
        if form.is_valid():
            kpi = form.save(commit=False)
            # Auto-calc threshold as 60% of max_score
            if kpi.max_score:
                kpi.goal_threshold = kpi.max_score * Decimal('0.6')
            kpi.save()
            messages.success(request, 'KPI created!')
            return redirect('kpi_list')
    else:
        form = PerformanceKPIForm()
    return render(request, 'masters/kpi_form.html', {'form': form})




def kpi_edit(request, pk):
    kpi = get_object_or_404(PerformanceKPI, pk=pk)
    if request.method == 'POST':
        # Manager can edit manually, no auto threshold calc
        form = PerformanceKPIForm(request.POST, instance=kpi)
        if form.is_valid():
            form.save()
            messages.success(request, 'KPI updated!')
            return redirect('kpi_list')
    else:
        form = PerformanceKPIForm(instance=kpi)
    return render(request, 'masters/kpi_form.html', {'form': form})



def kpi_view(request, pk):
    kpi = get_object_or_404(PerformanceKPI, pk=pk)
    form = PerformanceKPIForm(instance=kpi)
    return render(request, 'masters/kpi_form.html', {
        'form': form,
        'view_mode': True,  # flag to detect view mode in template
    })


from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import PerformanceKPI

def kpi_delete(request, pk):
    """
    Delete KPI directly when the modal 'Delete' link is clicked.
    The modal already asks for confirmation, so no extra page is needed.
    """
    kpi = get_object_or_404(PerformanceKPI, pk=pk)

    # Allow GET because the modal uses an <a href="..."> link
    if request.method in ['GET', 'POST']:
        kpi.delete()
        messages.success(request, f'KPI "{kpi.name}" deleted successfully!')
        return redirect('kpi_list')

    # Fallback in case of other methods
    messages.error(request, "Invalid request method.")
    return redirect('kpi_list')


def interviewround_list(request):
    rounds = InterviewRound.objects.all()
    return render(request, 'masters/interviewround_list.html', {'rounds': rounds})


def interviewround_create(request):
    if request.method == 'POST':
        form = InterviewRoundForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Interview Round created!')
            return redirect('interviewround_list')
    else:
        form = InterviewRoundForm()
    return render(request, 'masters/interviewround_form.html', {'form': form})




from django.shortcuts import get_object_or_404
def interviewround_view(request, pk):
    round_instance = get_object_or_404(InterviewRound, pk=pk)
    form = InterviewRoundForm(instance=round_instance)
    return render(request, 'masters/interviewround_form.html', {'form': form, 'view_mode': True})


def interviewround_edit(request, pk):
    round = get_object_or_404(InterviewRound, pk=pk)
    if request.method == 'POST':
        form = InterviewRoundForm(request.POST, instance=round)
        if form.is_valid():
            form.save()
            messages.success(request, 'Interview Round updated!')
            return redirect('interviewround_list')
    else:
        form = InterviewRoundForm(instance=round)
    return render(request, 'masters/interviewround_form.html', {'form': form})
def interviewround_delete(request, pk):
    round_instance = get_object_or_404(InterviewRound, pk=pk)
    if request.method == 'POST':
        round_instance.delete()
        messages.success(request, 'Interview Round deleted!')
    return redirect('interviewround_list')



from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import UserCustom
import re

# ----------------- AUTH VIEWS -----------------

def redirect_to_login(request):
    return redirect('login_view')

from django.http import HttpResponseRedirect
from django.urls import reverse

from django.shortcuts import render, redirect
from django.urls import reverse
from .models import UserCustom
from django.http import HttpResponseRedirect


def login_view(request):
    context = {}

    # ✅ Safely load users for dropdown (if your template uses it)
    try:
        context['users'] = UserCustom.objects.all()
    except Exception as e:
        print("LoginView: error loading users list:", e)
        context['users'] = []

    if request.method == "POST" and "password" in request.POST:
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()
        next_url = (
            request.POST.get("next")
            or request.GET.get("next")
            or reverse("dashboard")
        )
        context["selected_user"] = username

        try:
            # 👇 case-insensitive username match
            user = UserCustom.objects.get(username__iexact=username)
        except UserCustom.DoesNotExist:
            context["error"] = "Invalid credentials."
            return render(request, "registration/login.html", context)

        # 🔒 Check if account locked
        if getattr(user, "is_locked", False):
            context["error"] = "Account is locked. Contact admin."
            return render(request, "registration/login.html", context)

        # 🔑 Password check (your current plain-text logic)
        if user.password != password:
            user.wrong_attempts = (user.wrong_attempts or 0) + 1
            if user.wrong_attempts >= 3:
                user.is_locked = True
            user.save()
            context["error"] = "Invalid password."
            return render(request, "registration/login.html", context)

        # ✅ Successful login → reset wrong attempts
        user.wrong_attempts = 0
        user.save()

        # store session
        request.session["user_id"] = user.id
        request.session["username"] = user.username
        request.session["user_display_name"] = (
            user.get_full_name() if hasattr(user, "get_full_name") else user.username
        )

        response = HttpResponseRedirect(next_url)
        response.set_cookie("user_id", user.id)
        response.set_cookie("username", user.username)
        return response

    # GET → just show login page
    return render(request, "registration/login.html", context)




def set_passcode(request):
    username = request.COOKIES.get("username") or request.GET.get("username")
    if not username:
        return redirect("login_view")

    user = get_object_or_404(UserCustom, username=username)
    context = {"selected_user": username}

    if request.method == "POST":
        passcode = request.POST.get("passcode", "").strip()
        confirm = request.POST.get("confirm_passcode", "").strip()

        if passcode != confirm:
            context["error"] = "Passcodes do not match."
        elif not passcode.isdigit() or len(passcode) != 4:
            context["error"] = "Passcode must be exactly 4 digits."
        else:
            user.passcode = passcode
            user.passcode_set = True
            user.save()
            response = redirect("dashboard")
            return response

    return render(request, "registration/set_passcode.html", context)

def password_reset_view(request):
    context = {}
    username = request.POST.get("username") or request.GET.get("username")
    if username:
        username = username.strip()
    context["selected_user"] = username

    if not username:
        context["error"] = "Username is required."
        return render(request, "registration/password_reset.html", context)

    # Step 1: verify passcode
    if request.method == "POST" and "verify_passcode" in request.POST:
        passcode = request.POST.get("passcode", "").strip()
        try:
            user = UserCustom.objects.get(username=username)
            if not user.passcode_set:
                context["error"] = "Passcode not set. Please set a passcode first."
                return render(request, "registration/password_reset.html", context)
            if user.passcode and user.passcode.strip() == passcode:
                context["reset"] = True
                context["passcode_verified"] = True
            else:
                context["error"] = "Invalid passcode."
            return render(request, "registration/password_reset.html", context)
        except UserCustom.DoesNotExist:
            context["error"] = "User not found."
            return render(request, "registration/password_reset.html", context)

    # Step 2: reset password
    if request.method == "POST" and "password_reset_submit" in request.POST:
        new_pwd = request.POST.get("new_password", "").strip()
        confirm_pwd = request.POST.get("confirm_password", "").strip()
        try:
            user = UserCustom.objects.get(username=username)
            if new_pwd != confirm_pwd:
                context["reset"] = True
                context["passcode_verified"] = True
                context["error"] = "Passwords do not match."
            elif not re.match(r"^[A-Z][a-z]*[!@#$%^&*(),.?\":{}|<>][a-zA-Z0-9]*[0-9]+$", new_pwd):
                context["reset"] = True
                context["passcode_verified"] = True
                context["error"] = "Password must start with a capital letter, include lowercase, one special character, and one number. Length 8-16."
            else:
                user.password = new_pwd
                user.wrong_attempts = 0
                user.is_locked = False
                user.save()
                context["success_message"] = "Password reset successful. Please login."
                return render(request, "registration/login.html", context)
        except UserCustom.DoesNotExist:
            context["reset"] = True
            context["passcode_verified"] = True
            context["error"] = "User not found."
        return render(request, "registration/password_reset.html", context)

    # If GET request, show passcode reset form
    context["reset"] = True
    return render(request, "registration/password_reset.html", context)

def logout_view(request):
    # clear Django session
    request.session.flush()

    # clear our custom cookies
    response = redirect("login")
    response.delete_cookie("user_id")
    response.delete_cookie("username")

    return response


def master_dashboard(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login_view")
    user = UserCustom.objects.get(id=user_id)
    return render(request, "dashboard.html", {"user": user})






def user_list(request):
    context = {'users': UserCustom.objects.all()}
    if request.method == "POST" and "delete_user" in request.POST:
        user_id = request.POST.get("user_id")
        user = get_object_or_404(UserCustom, id=user_id)
        username = user.username
        user.delete()
        context["success_message"] = f"User {username} deleted successfully."
    return render(request, "masters/user_list.html", context)

from django.shortcuts import render, get_object_or_404, redirect
from .models import UserCustom
from .forms import UserAddForm, UserEditForm
import re

def user_form(request):
    if request.method == "POST":
        form = UserAddForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("user_list")
    else:
        form = UserAddForm()
    return render(request, "masters/user_form.html", {"form": form})


def user_view(request, user_id):
    user = get_object_or_404(UserCustom, id=user_id)
    form = UserEditForm(instance=user)
    # Disable all fields for view-only mode
    for field in form.fields.values():
        field.widget.attrs['readonly'] = True
        field.widget.attrs['disabled'] = True
    return render(
        request, "masters/user_form.html",
        {"form": form, "view_mode": True, "edit_mode": False}
    )


def user_edit(request, user_id):
    user = get_object_or_404(UserCustom, id=user_id)

    if request.method == "POST":
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            updated_user = form.save(commit=False)

            # Update password only if entered
            password = form.cleaned_data.get("password")
            if password:
                updated_user.password = password

            # Reset attempts if admin locks the account
            if updated_user.is_locked:
                updated_user.wrong_attempts = 0

            updated_user.save()
            return redirect("user_list")
    else:
        form = UserEditForm(instance=user)

    return render(
        request, "masters/user_form.html",
        {"form": form, "edit_mode": True, "view_mode": False}
    )



from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import UserCustom

def user_delete(request, user_id):
    user = get_object_or_404(UserCustom, id=user_id)
    user.delete()
    messages.success(request, f"User {user.username} has been deleted.")
    return redirect('user_list')
