from django.urls import path
from .views import CustomerListView

urlpatterns = [
    # path('<path>', views.<func>, name=''),  # template
    path('nhanvien/', CustomerListView.as_view(), name='api-nhanvien'),  # template
]