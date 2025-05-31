from django.urls import path
from .views import CustomerListView

urlpatterns = [
    # path('<path>', views.<func>, name=''),  # template
    path('khachhang/', CustomerListView.as_view(), name='api-khachhang'),  # template
]