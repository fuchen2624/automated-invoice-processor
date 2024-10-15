# Update ingestion/ocr_extract.py

import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import re
from datetime import datetime
import dateparser
from fuzzywuzzy import process
import os

import logging
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


def extract_text_from_image(image_path):
    return pytesseract.image_to_string(Image.open(image_path))

def extract_text_from_pdf(pdf_path):
    pages = convert_from_path(pdf_path)
    text = ""
    for page in pages:
        text += pytesseract.image_to_string(page)
    return text


def parse_float(s):
    return float(s.replace(',', '')) if s else None

def extract_invoice_data(text):
    # Extract invoice number and date
    invoice_number = re.search(r'Invoice No:\s*(\w+-\d+-\d+)', text)
    date = re.search(r'Date:\s*(\w+\s+\d{1,2},\s+\d{4})', text)
    total = re.search(r'Total Due:\s*\$?([\d,]+\.\d{2})', text)
    
    # Extract vendor and customer information as blocks
    from_block = re.search(r'From:(.*?)To:', text, re.DOTALL)
    to_block = re.search(r'To:(.*?)Description', text, re.DOTALL)
    
    vendor = from_block.group(1).strip() if from_block else None
    customer = to_block.group(1).strip() if to_block else None
    
    # Extract line items
    line_items = re.findall(r'(.+?)\s+(\d+)\s+\$([\d,]+\.\d{2})\s+\$([\d,]+\.\d{2})', text)
    
    return {
        'invoice_number': invoice_number.group(1) if invoice_number else None,
        'date': datetime.strptime(date.group(1), '%B %d, %Y').date() if date else None,
        'total_amount': parse_float(total.group(1)) if total else None,
        'vendor_name': vendor,
        'customer_name': customer,
        'line_items': [
            {
                'description': item[0].strip(),
                'quantity': int(item[1]),
                'unit_price': parse_float(item[2]),
                'total': parse_float(item[3])
            } for item in line_items
        ]
    }



def validate_extracted_data(data):
    errors = []
    if not data['invoice_number']:
        errors.append("Invoice number could not be extracted")
    if not data['date']:
        errors.append("Invoice date could not be extracted")
    if not data['total_amount']:
        errors.append("Total amount could not be extracted")
    if not data['vendor_name']:
        errors.append("Vendor name could not be extracted")
    return errors

def process_invoice(invoice_instance):
    try:
        file_path = invoice_instance.file.path
        file_extension = os.path.splitext(file_path)[1].lower()

        if file_extension == '.pdf':
            text = extract_text_from_pdf(file_path)
        elif file_extension in ['.jpg', '.jpeg', '.png']:
            text = extract_text_from_image(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")

        extracted_data = extract_invoice_data(text)

        print(extracted_data)

        validation_errors = validate_extracted_data(extracted_data)

        if validation_errors:
            processing_errors = ", ".join(validation_errors)
            invoice_instance.processing_errors = processing_errors
            
        
        print("Validation errors: ", validation_errors)

        # Update invoice instance with extracted data
        invoice_instance.invoice_number = extracted_data['invoice_number']
        invoice_instance.invoice_date = extracted_data['date']
        invoice_instance.total_amount = extracted_data['total_amount']
        invoice_instance.vendor_name = extracted_data['vendor_name']
        invoice_instance.processed = True
        invoice_instance.save()

        return extracted_data

    except Exception as e:
        logger.error(f"Error processing invoice {invoice_instance.id}: {str(e)}")
        invoice_instance.processed = False
        invoice_instance.save()
        raise
