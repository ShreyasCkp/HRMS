from django.contrib import admin
from .models import Department, Employee, Onboarding, Offboarding

admin.site.register(Department)
admin.site.register(Employee)
admin.site.register(Onboarding)
admin.site.register(Offboarding)
