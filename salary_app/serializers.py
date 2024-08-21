from rest_framework import serializers
from .models import Employee, SalarySlip, Notification

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id', 'employee_id', 'first_name', 'last_name', 'email', 'department', 'designation']
        read_only_fields = ['id']

class SalarySlipSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalarySlip
        fields = '__all__'
        read_only_fields = ['id', 'gross_earnings', 'total_deductions', 'net_salary']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'message', 'read', 'created_at']
        read_only_fields = ['id', 'created_at']
