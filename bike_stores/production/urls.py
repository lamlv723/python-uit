from django.urls import path
# Sử dụng import nhiều dòng để dễ đọc và quản lý khi có nhiều view
from .views import (
    ProductListView,
    ProductDetailView,
    StockListView,
    StockDetailView,
)

urlpatterns = [
    # Product API
    # Sử dụng định dạng nhiều dòng cho các hàm path() để rõ ràng, nhất quán
    path(
        "products/",
        ProductListView.as_view(),
        name="product-list-create"
    ),  # GET: list, POST: create

    path(
        "products/<int:product_id>/",
        ProductDetailView.as_view(),
        name="product-detail"
    ),  # GET: detail, PATCH: update, DELETE: delete

    # Stock API
    path(
        "stocks/",
        StockListView.as_view(),
        name="stock-list-create"
    ),  # GET: list, POST: create

    path(
        "stocks/<int:store_id>/<int:product_id>/",
        StockDetailView.as_view(),
        name="stock-detail"
    ),  # GET: detail, PATCH: update, DELETE: delete
]