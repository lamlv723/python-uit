from django.urls import path
from .views import (
    InventoryReportView
    , RevenueOverTimeReportView
)

urlpatterns = [
    # path('<path>/', views.<func>, name=''),  # template
    path('inventory-by-store/', InventoryReportView.as_view(), name='inventory_by_store'),
    path('revenue-over-time/', RevenueOverTimeReportView.as_view(), name='revenue-over-time'),
]