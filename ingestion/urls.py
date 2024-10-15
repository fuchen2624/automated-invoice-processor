from django.urls import path
from .views import InvoiceUploadView, upload_success, InvoiceListView, InvoiceSearchView

urlpatterns = [
    path('upload/', InvoiceUploadView.as_view(), name='upload_invoice'),
    path('success/', upload_success, name='upload_success'),
    path('invoices/', InvoiceListView.as_view(), name='invoice_list'),
    path('search/', InvoiceSearchView.as_view(), name='invoice_search'),
]