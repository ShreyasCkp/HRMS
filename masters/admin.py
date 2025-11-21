from django.contrib import admin
from .models import Department, JobRole, LeaveType, PerformanceKPI, InterviewRound, Workspace, OfficeEvent

admin.site.register(Department)
admin.site.register(JobRole)
admin.site.register(LeaveType)
admin.site.register(PerformanceKPI)
admin.site.register(InterviewRound)
admin.site.register(Workspace)
admin.site.register(OfficeEvent)
