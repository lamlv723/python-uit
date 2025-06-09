from django.urls import path
from .views import (
    InventoryReportView
    , RevenueReportView
    , CustomerReportView
)

urlpatterns = [
    # path('<path>/', views.<func>, name=''),  # template
    path('inventory-by-store/', InventoryReportView.as_view(), name='inventory_by_store'),
    path('revenue-over-time/', RevenueReportView.as_view(), name='revenue-over-time'),
    path('customer-analysis/', CustomerReportView.as_view(), name='customer-analysis'),
]