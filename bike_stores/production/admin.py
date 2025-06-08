# your_project/production/admin.py

from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from .models import Category, Brand, Product, Stock

# --- Lớp PriceRangeFilter cho Product ---
class PriceRangeFilter(admin.SimpleListFilter):
    title = 'Khoảng giá'
    parameter_name = 'price_range'

    def lookups(self, request, model_admin):
        return [
            ('0-100', 'Dưới 100'),
            ('100-500', '100 - 500'),
            ('500-1000', '500 - 1000'),
            ('1000-max', 'Trên 1000'),
        ]

    def queryset(self, request, queryset):
        if self.value() == '0-100':
            return queryset.filter(list_price__lt=100)
        if self.value() == '100-500':
            return queryset.filter(list_price__gte=100, list_price__lt=500)
        if self.value() == '500-1000':
            return queryset.filter(list_price__gte=500, list_price__lte=1000)
        if self.value() == '1000-max':
            return queryset.filter(list_price__gte=1000)
        return queryset

# --- Các lớp Admin tùy chỉnh ---

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_id', 'product_name', 'get_brand_name', 'get_category_name', 'model_year', 'list_price')
    list_filter = ('brand_id', 'category_id', 'model_year', PriceRangeFilter)
    search_fields = ('product_name',)
    ordering = ('product_name',)
    search_placeholder = "Search the product here"

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['search_placeholder'] = self.search_placeholder
        return super().changelist_view(request, extra_context=extra_context)

    @admin.display(description='Brand', ordering='brand_id__brand_name')
    def get_brand_name(self, obj):
        return obj.brand_id.brand_name

    @admin.display(description='Category', ordering='category_id__category_name')
    def get_category_name(self, obj):
        return obj.category_id.category_name

class BrandAdmin(admin.ModelAdmin):
    list_display = ('brand_id', 'brand_name')
    search_fields = ('brand_name',)
    ordering = ('brand_name',)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_id', 'category_name')
    search_fields = ('category_name',)
    ordering = ('category_name',)

class StockAdmin(admin.ModelAdmin):
    list_display = ('get_product_name', 'get_store_name', 'quantity')
    search_fields = ('product_id__product_name', 'store_id__store_name')
    list_filter = ('store_id', 'product_id__category_id', 'product_id__brand_id')
    ordering = ('store_id', 'product_id__product_name')

    @admin.display(description='Product Name', ordering='product_id__product_name')
    def get_product_name(self, obj):
        return obj.product_id.product_name

    @admin.display(description='Store Name', ordering='store_id__store_name')
    def get_store_name(self, obj):
        return obj.store_id.store_name

# --- Đăng ký Model với các lớp Admin tương ứng ---
admin.site.register(Product, ProductAdmin)
admin.site.register(Brand, BrandAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Stock, StockAdmin)