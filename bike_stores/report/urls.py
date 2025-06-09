from django.urls import path
from .views import (
    InventoryReportView
    , RevenueReportView
    , CustomerReportView
)

urlpatterns = [
    # path('<path>/', views.<func>, name=''),  # template
    path('inventory-report/', InventoryReportView.as_view(), name='inventory-report'),
    path('revenue-report/', RevenueReportView.as_view(), name='revenue-report'),
    path('customer-analysis/', CustomerReportView.as_view(), name='customer-analysis'),
]