from django.shortcuts import render, redirect
from .models import LeaveRequest, LeaveType
from .forms import LeaveRequestForm, LeaveTypeForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def leave_list(request):
    leaves = LeaveRequest.objects.select_related('employee', 'leave_type').all()
    return render(request, 'leave_management/leave_list.html', {'leaves': leaves})


def leave_create(request):
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Leave request submitted!')
            return redirect('leave_list')
    else:
        form = LeaveRequestForm()
    return render(request, 'leave_management/leave_form.html', {'form': form})


def leave_type_list(request):
    types = LeaveType.objects.all()
    return render(request, 'leave_management/leave_type_list.html', {'types': types})


def leave_type_create(request):
    if request.method == 'POST':
        form = LeaveTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Leave type added!')
            return redirect('leave_type_list')
    else:
        form = LeaveTypeForm()
    return render(request, 'leave_management/leave_type_form.html', {'form': form})
