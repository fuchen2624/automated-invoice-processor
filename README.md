# Automated Invoice Processor

## Overview

This project is a demonstration of an automated invoice processing system. It provides the minimal features needed for automated invoice processing and can serve as a starting point for those looking to automate their own invoice workflows.

## Features

- Invoice ingestion from email attachments and manual uploads
- OCR (Optical Character Recognition) for extracting text from PDF and image invoices
- Data extraction and validation for key invoice fields
- Basic error handling and reporting
- Simple search functionality using ElasticSearch
- Web interface for uploading invoices and viewing processed results

## Tech Stack

- Backend: Python 3.x with Django
- Database: SQLite (for simplicity, can be easily switched to PostgreSQL for production)
- OCR: Tesseract (via pytesseract)
- PDF Processing: pdf2image
- Task Queue: Celery with Redis as the message broker
- Search: ElasticSearch with django-elasticsearch-dsl
- Frontend: Django templates (basic HTML/CSS)

## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.x
- pip (Python package manager)
- Redis server
- Tesseract OCR
- ElasticSearch
- (Optional) MacPorts (if you're using macOS and prefer it over Homebrew)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/fuchen2624/automated-invoice-processor.git
   cd automated-invoice-processor
   ```

2. Create a virtual environment and activate it:
   ```
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

4. Apply database migrations:
   ```
   python manage.py migrate
   ```

5. Create a superuser for the Django admin interface:
   ```
   python manage.py createsuperuser
   ```

6. Build the ElasticSearch index:
   ```
   python manage.py search_index --rebuild
   ```

## Configuration 

### Email Configuration (Optional)

To enable automatic email checking for invoices, you need to set up a `.env` file in the root directory of the project with your email credentials:

1. Create a file named `.env` in the project root.
2. Add the following content to the file:
   ```
   EMAIL_HOST=your_email_host
   EMAIL_USER=your_email_username
   EMAIL_PASSWORD=your_email_password
   ```
   Replace `your_email_host`, `your_email_username`, and `your_email_password` with your actual email server details.

3. Make sure to add `.env` to your `.gitignore` file to avoid committing sensitive information.

## Running the Application

1. Start the Redis server (if not already running)

2. Start the Celery worker:
   ```
   celery -A invoice_processor worker -l info
   ```

3. Start the Celery beat scheduler:
   ```
   celery -A invoice_processor beat -l info
   ```

4. Run the Django development server:
   ```
   python manage.py runserver
   ```

5. Access the application at `http://localhost:8000`

## Usage

1. Upload invoices through the web interface at `http://localhost:8000/ingestion/upload/`
2. View processed invoices and search results at `http://localhost:8000/ingestion/search/`
3. Access the admin interface at `http://localhost:8000/admin/` to manage invoices and other data
4. The system will automatically check for new invoices in the configured email account at regular intervals

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open-source and available under the [MIT License](LICENSE).

## Disclaimer

This is a demonstration project and may not be suitable for production use without further development and security enhancements. Use at your own risk.