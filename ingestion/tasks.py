# In ingestion/tasks.py

import imaplib
import email
from celery import shared_task
from django.core.files.base import ContentFile
from .models import Invoice
import os
from dotenv import load_dotenv
from .ocr_extract import process_invoice

from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def process_invoice_task(self, invoice_id):
    try:
        invoice = Invoice.objects.get(id=invoice_id)
        process_invoice(invoice)
    except Invoice.DoesNotExist:
        logger.error(f"Invoice with id {invoice_id} does not exist.")
    except ValidationError as ve:
        logger.error(f"Validation error processing invoice {invoice_id}: {str(ve)}")
        raise self.retry(exc=ve, countdown=60*5)  # Retry after 5 minutes
    except Exception as e:
        logger.error(f"Error processing invoice {invoice_id}: {str(e)}")
        raise self.retry(exc=e, countdown=60*15)  # Retry after 15 minutes


@shared_task
def check_email_for_invoices():
    # Load environment variables
    load_dotenv()

    # Email configuration
    EMAIL_HOST = os.getenv('EMAIL_HOST')
    EMAIL_USER = os.getenv('EMAIL_USER')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

    # Connect to the email server
    mail = imaplib.IMAP4_SSL(EMAIL_HOST)
    mail.login(EMAIL_USER, EMAIL_PASSWORD)
    mail.select('inbox')

    # Search for unread emails with attachments
    _, message_numbers = mail.search(None, '(UNSEEN)')
    for num in message_numbers[0].split():
        _, msg = mail.fetch(num, '(RFC822)')
        email_body = msg[0][1]
        email_message = email.message_from_bytes(email_body)

        # Process attachments
        for part in email_message.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue

            filename = part.get_filename()
            if filename and filename.lower().endswith(('.pdf', '.jpg', '.png', '.jpeg')):
                file_data = part.get_payload(decode=True)
                file_content = ContentFile(file_data, name=filename)
                
                # Save the attachment as an Invoice object
                invoice = Invoice(file=file_content)
                invoice.save()

                # Process the invoice
                print(f"Processing invoice {invoice.id}")
                process_invoice_task.delay(invoice.id)

        # Mark the email as read
        mail.store(num, '+FLAGS', '\\Seen')

    mail.close()
    mail.logout()