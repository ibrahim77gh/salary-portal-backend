from django.db import models
from django.utils import timezone
from django.conf import settings
from datetime import datetime

class Employee(models.Model):
    employee_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    department = models.CharField(max_length=100, null=True, blank=True)
    designation = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.employee_id})"

class SalarySlip(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    month = models.DateField(default=datetime.now)
    
    # Earnings
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    conveyance_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    medical_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gross_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)
    
    # Deductions
    provident_fund = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    professional_tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    income_tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)

    # Net Salary
    net_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)

    def save(self, *args, **kwargs):
        # Calculate gross earnings
        self.gross_earnings = (
            self.basic_salary +
            self.conveyance_allowance +
            self.medical_allowance +
            self.other_allowances
        )

        # Calculate total deductions
        self.total_deductions = (
            self.provident_fund +
            self.professional_tax +
            self.income_tax +
            self.other_deductions
        )

        # Calculate net salary
        self.net_salary = self.gross_earnings - self.total_deductions
        
        super(SalarySlip, self).save(*args, **kwargs)

    def __str__(self):
        return f"Salary Slip for {self.employee} - {self.month.strftime('%B %Y')}"

class UploadLog(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='uploads', null=True, blank=True)
    upload_time = models.DateTimeField(default=timezone.now)
    file_name = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING', null=True, blank=True)
    total_records = models.IntegerField(null=True, blank=True)
    processed_records = models.IntegerField(default=0, null=True, blank=True)
    error_log = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Upload Log: {self.file_name} by {self.user} at {self.upload_time}"

class ColumnMapping(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    active = models.BooleanField(default=False)
    employee_id = models.CharField(max_length=100, default='Employee ID')
    first_name = models.CharField(max_length=100, default='First Name')
    last_name = models.CharField(max_length=100, default='Last Name')
    email = models.CharField(max_length=100, default='Email')
    basic_salary = models.CharField(max_length=100, default='Basic Salary')
    conveyance_allowance = models.CharField(max_length=100, default='Conveyance Allowance')
    medical_allowance = models.CharField(max_length=100, default='Medical Allowance')
    other_allowances = models.CharField(max_length=100, default='Other Allowances')
    provident_fund = models.CharField(max_length=100, default='Provident Fund')
    professional_tax = models.CharField(max_length=100, default='Professional Tax')
    income_tax = models.CharField(max_length=100, default='Income Tax')
    other_deductions = models.CharField(max_length=100, default='Other Deductions')

    def __str__(self):
        return f"Column Mapping for {self.user} (Active: {self.active})"
