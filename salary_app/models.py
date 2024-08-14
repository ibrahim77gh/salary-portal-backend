from django.db import models
from django.utils import timezone
from django.conf import settings

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
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SENT', 'Sent'),
        ('FAILED', 'Failed'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='salary_slips', null=True, blank=True)
    month = models.DateField(null=True, blank=True)
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    allowances = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    pdf = models.FileField(upload_to='salary_slips/', null=True, blank=True)
    email_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.net_salary:
            self.net_salary = (self.basic_salary or 0) + (self.allowances or 0) - (self.deductions or 0)
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
        return f"Upload Log: {self.file_name} by {self.uploaded_by} at {self.upload_time}"
