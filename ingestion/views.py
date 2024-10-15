from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.views import View

from .models import Invoice
from .forms import InvoiceForm
from .tasks import process_invoice_task
from django.views.generic import ListView
from elasticsearch_dsl import Q
from .documents import InvoiceDocument

class InvoiceSearchView(ListView):
    template_name = 'ingestion/invoice_search.html'
    context_object_name = 'invoices'
    paginate_by = 20

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if query:
            q = Q('multi_match', query=query, fields=['invoice_number', 'vendor_name'])
            search = InvoiceDocument.search().query(q)
            return search.to_queryset()
        return Invoice.objects.all()

class InvoiceListView(ListView):
    model = Invoice
    template_name = 'ingestion/invoice_list.html'
    context_object_name = 'invoices'
    ordering = ['-uploaded_at']

class InvoiceUploadView(View):
    def get(self, request):
        form = InvoiceForm()
        return render(request, 'ingestion/upload.html', {'form': form})

    def post(self, request):
        form = InvoiceForm(request.POST, request.FILES)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.source = 'UPLOAD'
            invoice.save()

            # Process the invoice
            print(f"Processing invoice {invoice.id}")
            process_invoice_task.delay(invoice.id)
            
            return redirect('upload_success')
        return render(request, 'ingestion/upload.html', {'form': form})

def upload_success(request):
    return render(request, 'ingestion/success.html')