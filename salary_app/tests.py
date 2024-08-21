from django.test import TestCase

# Create your tests here.
from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import Employee, SalarySlip, ColumnMapping, UploadLog
from .tasks import generate_and_send_salary_slips


class APITestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        UserModel = get_user_model()
        self.user = UserModel.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.client.force_authenticate(user=self.user)

        # Create a sample employee
        self.employee = Employee.objects.create(
            employee_id='E001',
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com'
        )

        # Create a sample salary slip
        self.salary_slip = SalarySlip.objects.create(
            employee=self.employee,
            month='2024-08-01',
            basic_salary=50000,
            conveyance_allowance=2000,
            medical_allowance=1500,
            other_allowances=1000,
            provident_fund=2000,
            professional_tax=500,
            income_tax=3000,
            other_deductions=1000
        )

class ExcelUploadAPITestCase(APITestCase):

    def test_upload_excel(self):
        url = reverse('excelupload')  # Replace with the actual URL name for your endpoint
        excel_file = SimpleUploadedFile(
            'test_file.xlsx',
            b"""Excel file content in binary format""",
            content_type='application/vnd.ms-excel'
        )

        response = self.client.post(url, {'file': excel_file}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(UploadLog.objects.count(), 1)
        self.assertEqual(SalarySlip.objects.count(), 2)

class EmployeeListAPITestCase(APITestCase):

    def test_list_employees(self):
        url = reverse('employee-list')  # Replace with the actual URL name for your endpoint

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['first_name'], self.employee.first_name)
        self.assertEqual(response.data[0]['email'], self.employee.email)

class GenerateSalarySlipTestCase(APITestCase):

    def test_generate_and_send_salary_slips(self):
        slip_ids = [self.salary_slip.id]
        task_result = generate_and_send_salary_slips.apply(args=[slip_ids])

        self.assertTrue(task_result.successful())
        # Further assertions can check if the PDF was generated and if emails were sent
