from django.contrib import admin
from .models import Employee, SalarySlip, UploadLog

# Register your models here.
@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'first_name', 'last_name', 'email', 'department', 'designation')

@admin.register(SalarySlip)
class SalarySlipAdmin(admin.ModelAdmin):
    list_display = ('employee', 'month', 'net_salary')
    list_filter = ('month',)

@admin.register(UploadLog)
class UploadLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'file_name', 'status', 'total_records', 'processed_records', 'error_log')
    list_filter = ('status', 'user')