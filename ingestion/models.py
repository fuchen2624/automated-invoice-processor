from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class Invoice(models.Model):
    file = models.FileField(upload_to='invoices/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    source = models.CharField(max_length=10, choices=[('EMAIL', 'Email'), ('UPLOAD', 'Manual Upload')], default='UPLOAD')

   # New fields for extracted data
    invoice_number = models.CharField(max_length=50, blank=True, null=True)
    invoice_date = models.DateField(blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    vendor_name = models.CharField(max_length=100, blank=True, null=True)

    processing_errors = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Invoice {self.invoice_number} from {self.vendor_name}"
    

@receiver(post_save, sender=Invoice)
def update_elasticsearch(sender, instance, **kwargs):
    from .documents import InvoiceDocument
    InvoiceDocument().update(instance)