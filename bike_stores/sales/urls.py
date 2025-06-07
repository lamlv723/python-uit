from django.urls import path
from .views import (
    CustomerListView, CustomerDetailView,
    OrderListView, OrderDetailView,
    OrderItemListView, OrderItemDetailView,
    StaffListView, StaffDetailView,
    StoreListView, StoreDetailView
)

urlpatterns = [
    # CustomerListView
    path('customer/', CustomerListView.as_view(), name='customer-list'),  # GET
    path('customer/create/', CustomerListView.as_view(), name='customer-list-create'),  # POST
    # CustomerDetailView
    path('customer/<int:customer_id>/', CustomerDetailView.as_view(), name='customer-detail'),  # GET with param
    path('customer/update/<int:customer_id>/', CustomerDetailView.as_view(), name='customer-detail'),  # PATCH with param
    path('customer/delete/<int:customer_id>/', CustomerDetailView.as_view(), name='customer-detail'),  # DELETE with param

    # Orders
    path('orders/', OrderListView.as_view(), name='order-list'),  # GET, POST
    path('orders/<int:order_id>/', OrderDetailView.as_view(), name='order-detail'),  # GET, PATCH, DELETE

    # Order Items
    path('order-items/', OrderItemListView.as_view(), name='orderitem-list'),  # GET, POST
    path('order-items/<int:order_id>/<int:item_id>/', OrderItemDetailView.as_view(), name='orderitem-detail'),  # GET, PATCH, DELETE

    # Staffs
    path('staffs/', StaffListView.as_view(), name='staff-list'),  # GET, POST
    path('staffs/<int:staff_id>/', StaffDetailView.as_view(), name='staff-detail'),  # GET, PATCH, DELETE

    # Stores
    path('stores/', StoreListView.as_view(), name='store-list'),  # GET, POST
    path('stores/<int:store_id>/', StoreDetailView.as_view(), name='store-detail'),  # GET, PATCH, DELETE
]