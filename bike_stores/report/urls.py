from django.urls import path
from .views import (
    InventoryReportView
    , RevenueReportView
    , CustomerAnalysisView
)

urlpatterns = [
    # path('<path>/', views.<func>, name=''),  # template
    path('inventory-report/', InventoryReportView.as_view(), name='inventory-report'),
    path('revenue-report/', RevenueReportView.as_view(), name='revenue-report'),
    path('customer-analysis/', CustomerAnalysisView.as_view(), name='customer-analysis'),
]