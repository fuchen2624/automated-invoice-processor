from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import Invoice

@registry.register_document
class InvoiceDocument(Document):
    class Index:
        name = 'invoices'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }

    invoice_number = fields.TextField()
    vendor_name = fields.TextField()
    invoice_date = fields.DateField()
    total_amount = fields.FloatField()
    source = fields.KeywordField()
    processed = fields.BooleanField()
    processing_errors = fields.TextField()

    class Django:
        model = Invoice
        fields = [
            'id',
        ]