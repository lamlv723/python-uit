from django.urls import path
from .views import CustomerListView, CustomerDetailView

urlpatterns = [
    # path('<path>', views.<func>, name=''),  # template
    # CustomerListView
    path('customer/', CustomerListView.as_view(), name='customer-list'),  # GET
    path('customer/create/', CustomerListView.as_view(), name='customer-list-create'),  # POST
    # CustomerDetailView
    path('customer/<int:customer_id>/', CustomerDetailView.as_view(), name='customer-detail'),  # GET with param
    path('customer/update/<int:customer_id>/', CustomerDetailView.as_view(), name='customer-detail'),  # PATCH with param
    path('customer/delete/<int:customer_id>/', CustomerDetailView.as_view(), name='customer-detail'),  # DELETE with param
]