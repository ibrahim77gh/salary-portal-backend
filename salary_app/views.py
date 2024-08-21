from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

import pandas as pd
from datetime import datetime

from .models import Employee, SalarySlip, UploadLog, ColumnMapping, Notification
from .tasks import generate_and_send_salary_slips
from .serializers import EmployeeSerializer, SalarySlipSerializer, NotificationSerializer, UploadLogSerializer

class EmployeeViewSet(ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]

class SalarySlipViewSet(ModelViewSet):
    queryset = SalarySlip.objects.all()
    serializer_class = SalarySlipSerializer
    permission_classes = [IsAuthenticated]

class NotificationViewSet(ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Return notifications only for the currently authenticated user
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')

class UploadLogViewSet(ModelViewSet):
    serializer_class = UploadLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Return upload logs only for the currently authenticated user
        return UploadLog.objects.filter(user=self.request.user).order_by('-upload_time')
    
class MarkNotificationsReadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Get all unread notifications for the current user
        unread_notifications = Notification.objects.filter(user=request.user, read=False)

        # Mark all unread notifications as read
        unread_notifications.update(read=True)

        # Return a response indicating success
        return Response({"message": "All notifications marked as read."}, status=status.HTTP_200_OK)

class ExcelUploadAPIView(APIView):
    def post(self, request):
        # Fetch the uploaded file from the request
        excel_file = request.FILES.get('file')
        if not excel_file:
            print('No file uploaded')
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            print('Excel file uploaded:', excel_file.name)

        # Fetch user-specific active column mappings
        user = request.user
        try:
            column_mapping = ColumnMapping.objects.filter(user=user, active=True).first()
            if not column_mapping:
                # Use default column mapping if no active mapping found
                column_mapping = ColumnMapping(user=user)
        except ColumnMapping.DoesNotExist:
            # Use default column mapping if user-specific mapping does not exist
            column_mapping = ColumnMapping(user=user)

        column_mapping_dict = {
            'employee_id': column_mapping.employee_id,
            'first_name': column_mapping.first_name,
            'last_name': column_mapping.last_name,
            'email': column_mapping.email,
            'basic_salary': column_mapping.basic_salary,
            'conveyance_allowance': column_mapping.conveyance_allowance,
            'medical_allowance': column_mapping.medical_allowance,
            'other_allowances': column_mapping.other_allowances,
            'provident_fund': column_mapping.provident_fund,
            'professional_tax': column_mapping.professional_tax,
            'income_tax': column_mapping.income_tax,
            'other_deductions': column_mapping.other_deductions
        }

        # Save upload log entry
        upload_log = UploadLog.objects.create(
            user=user,
            file_name=excel_file.name,
            status='PENDING',
            total_records=0,
            processed_records=0,
            error_log=''
        )

        # Read the Excel file into a pandas DataFrame
        df = pd.read_excel(excel_file)
        print(df.head())

        def get_column(df, column_name):
            if column_name in df.columns:
                return df[column_name]
            return None

        # Extract columns based on user-defined or default names
        employee_ids = get_column(df, column_mapping_dict['employee_id'])
        first_names = get_column(df, column_mapping_dict['first_name'])
        last_names = get_column(df, column_mapping_dict['last_name'])
        emails = get_column(df, column_mapping_dict['email'])
        basic_salaries = get_column(df, column_mapping_dict['basic_salary'])
        conveyance_allowances = get_column(df, column_mapping_dict['conveyance_allowance'])
        medical_allowances = get_column(df, column_mapping_dict['medical_allowance'])
        other_allowances = get_column(df, column_mapping_dict['other_allowances'])
        provident_funds = get_column(df, column_mapping_dict['provident_fund'])
        professional_taxes = get_column(df, column_mapping_dict['professional_tax'])
        income_taxes = get_column(df, column_mapping_dict['income_tax'])
        other_deductions = get_column(df, column_mapping_dict['other_deductions'])

        if employee_ids is None:
            raise ValueError("Employee ID column not found in Excel file")

        total_records = len(employee_ids)
        upload_log.total_records = total_records
        upload_log.save()

        slip_ids = []

        # Iterate over the rows and create/update employee and salary slip records
        for i in range(total_records):
            try:
                employee, created = Employee.objects.get_or_create(
                    employee_id=employee_ids[i],
                    defaults={
                        'first_name': first_names[i] if first_names is not None else '',
                        'last_name': last_names[i] if last_names is not None else '',
                        'email': emails[i] if emails is not None else '',
                    }
                )

                basic_salary = basic_salaries[i] if basic_salaries is not None else 0
                conveyance_allowance = conveyance_allowances[i] if conveyance_allowances is not None else 0
                medical_allowance = medical_allowances[i] if medical_allowances is not None else 0
                other_allowance = other_allowances[i] if other_allowances is not None else 0

                provident_fund = provident_funds[i] if provident_funds is not None else 0
                professional_tax = professional_taxes[i] if professional_taxes is not None else 0
                income_tax = income_taxes[i] if income_taxes is not None else 0
                other_deduction = other_deductions[i] if other_deductions is not None else 0

                salary_slip = SalarySlip.objects.create(
                    employee=employee,
                    month=datetime.now(),  # Placeholder for the current month
                    basic_salary=float(basic_salary),
                    conveyance_allowance=float(conveyance_allowance),
                    medical_allowance=float(medical_allowance),
                    other_allowances=float(other_allowance),
                    provident_fund=float(provident_fund),
                    professional_tax=float(professional_tax),
                    income_tax=float(income_tax),
                    other_deductions=float(other_deduction),
                )
                upload_log.processed_records += 1
                upload_log.save()
                slip_ids.append(salary_slip.id)
            except Exception as e:
                upload_log.error_log += f"Error processing row {i + 1}: {str(e)}\n"
                upload_log.save()

        upload_log.status = 'COMPLETED'
        upload_log.save()

        # Trigger the Celery task to generate and send the salary slips
        print(slip_ids)
        generate_and_send_salary_slips.delay(slip_ids, user.id)

        return Response({'message': 'Excel file processed successfully, background task started for salary slip generation'}, status=status.HTTP_200_OK)
    