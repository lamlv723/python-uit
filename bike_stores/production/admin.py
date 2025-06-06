# your_project/production/admin.py

from django.contrib import admin
from django.contrib.admin import SimpleListFilter # Cần import này để tạo bộ lọc khoảng giá tùy chỉnh
from django.db.models import F # Có thể hữu ích cho sắp xếp phức tạp hoặc tính toán
from .models import Category, Brand, Product, Stock

# 1. Định nghĩa bộ lọc tùy chỉnh cho khoảng giá (Tính năng số 3)
class PriceRangeFilter(SimpleListFilter):
    title = 'Khoảng giá' # Tiêu đề hiển thị trên thanh bên phải của Admin UI
    parameter_name = 'price_range' # Tên parameter trong URL

    def lookups(self, request, model_admin):
        """
        Trả về danh sách các tuples:
        (giá trị sẽ xuất hiện trong URL, tên hiển thị trên UI)
        """
        return [
            ('0-100', 'Dưới 100'),
            ('100-500', '100 - 500'),
            ('500-1000', '500 - 1000'),
            ('1000-max', 'Trên 1000'),
        ]

    def queryset(self, request, queryset):
        """
        Trả về queryset đã lọc dựa trên giá trị đã chọn.
        """
        if self.value() == '0-100':
            return queryset.filter(list_price__lt=100)
        if self.value() == '100-500':
            return queryset.filter(list_price__gte=100, list_price__lt=500)
        if self.value() == '500-1000':
            return queryset.filter(list_price__gte=500, list_price__lt=1000)
        if self.value() == '1000-max':
            return queryset.filter(list_price__gte=1000)
        return queryset # Trả về queryset gốc nếu không có giá trị nào được chọn

# 2. Định nghĩa lớp ProductAdmin tùy chỉnh
class ProductAdmin(admin.ModelAdmin):
    # a. Hiển thị các cột mong muốn trong danh sách
    list_display = (
        'product_id', 'product_name', 'brand_id', 'category_id', # Hiển thị các trường khóa ngoại
        'model_year', 'list_price'
    )

    # b. Thêm các bộ lọc vào thanh bên phải của Admin UI (Tính năng 1 & 2)
    list_filter = (
        'brand_id',    # Lọc theo Brand
        'category_id', # Lọc theo Category
        'model_year',  # Lọc theo Model Year (cũng hữu ích)
        PriceRangeFilter, # Kích hoạt bộ lọc khoảng giá tùy chỉnh
    )

    # c. Thêm ô tìm kiếm (nếu chưa có)
    search_fields = ('product_name',) # Cho phép tìm kiếm theo tên sản phẩm

    # d. Sắp xếp mặc định của danh sách (Tính năng 4)
    # Bạn có thể sắp xếp theo một hoặc nhiều trường.
    # Sử dụng '-' trước tên trường để sắp xếp giảm dần.
    ordering = ('product_name',) # Mặc định sắp xếp tăng dần theo tên sản phẩm
    # Hoặc: ordering = ('-list_price',) để sắp xếp giảm dần theo giá
    # Hoặc: ordering = ('brand_id__brand_name', 'product_name') để sắp xếp theo tên brand, sau đó theo tên sản phẩm

    # Optional: Thêm các action tùy chỉnh nếu bạn muốn
    # actions = [your_custom_action_function]

# 3. Đăng ký các Model với lớp Admin tương ứng
# Đăng ký Product với lớp ProductAdmin tùy chỉnh của bạn
admin.site.register(Product, ProductAdmin)

# Đăng ký các Model còn lại như bình thường
admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(Stock)