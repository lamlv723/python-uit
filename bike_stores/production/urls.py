from django.urls import path
from .views import ProductListView, ProductDetailView, StockListView, StockDetailView # <--- Dòng này đã được thêm vào/kiểm tra lại

urlpatterns = [
    # path('<path>/', views.<func>, name=''), # template

    # Product API
    path('products/', ProductListView.as_view(), name='product-list-create'), # GET: list, POST: create
    path('products/<int:product_id>/', ProductDetailView.as_view(), name='product-detail'), # GET: detail, PATCH: update, DELETE: delete

    # Stock API
    path('stocks/', StockListView.as_view(), name='stock-list-create'), # GET: list, POST: create
    path('stocks/<int:store_id>/<int:product_id>/', StockDetailView.as_view(), name='stock-detail'), # GET: detail, PATCH: update, DELETE: delete
]