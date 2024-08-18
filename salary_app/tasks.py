from celery import shared_task
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from weasyprint import HTML
import os
from .models import SalarySlip
import logging

logger = logging.getLogger(__name__)

@shared_task
def generate_and_send_salary_slips(slip_ids):
    slips = SalarySlip.objects.filter(id__in=slip_ids)
    logger.info("Starting the salary slip generation task")
    for slip in slips:
        try:
            # Prepare the data for the template
            context = {
                'employee_id': slip.employee.employee_id,
                'first_name': slip.employee.first_name,
                'last_name': slip.employee.last_name,
                'email': slip.employee.email,
                'basic_salary': slip.basic_salary,
                'conveyance_allowance': slip.conveyance_allowance,
                'medical_allowance': slip.medical_allowance,
                'other_allowances': slip.other_allowances,
                'gross_earnings': slip.gross_earnings,
                'provident_fund': slip.provident_fund,
                'professional_tax': slip.professional_tax,
                'income_tax': slip.income_tax,
                'other_deductions': slip.other_deductions,
                'total_deductions': slip.total_deductions,
                'net_salary': slip.net_salary,
                'month': slip.month.strftime('%B %Y'),
            }

            # Render the HTML template with context
            template_path = os.path.join(settings.BASE_DIR, 'templates/salary_slip.html')
            html_string = render_to_string(template_path, context)
            html = HTML(string=html_string)
            
            # Generate PDF
            pdf_file = html.write_pdf()

            # Send email with PDF attachment
            subject = f'Salary Slip for {context["month"]}'
            email = EmailMessage(
                subject,
                f'Dear {context["first_name"]},\n\nPlease find attached your salary slip for {context["month"]}.',
                'hr@example.com',
                [context['email']]
            )
            email.attach(f'Salary_Slip_{context["month"]}.pdf', pdf_file, 'application/pdf')
            email.send()
            logger.info(f"Salary slip sent to {context['email']} for {context['month']}")

            # Optionally update the status of the SalarySlip
            slip.status = 'SENT'
            slip.save()

        except Exception as e:
            # Handle or log the exception
            slip.status = 'ERROR'
            slip.error_log = str(e)
            logger.info(f"ERROR: {str(e)}")
            logger.error(str(e))
            slip.save()
