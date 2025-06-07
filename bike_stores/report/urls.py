from django.urls import path
from .views import (
    InventoryReportView
    , SalesOverTimeReportView
)

urlpatterns = [
    # path('<path>/', views.<func>, name=''),  # template
    path('inventory-by-store/', InventoryReportView.as_view(), name='inventory_by_store'),
    path('sales-over-time/', SalesOverTimeReportView.as_view(), name='sales-over-time'),
]