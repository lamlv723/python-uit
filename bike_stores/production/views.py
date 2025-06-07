from django.views import View
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from django.db.models import F
import json
from decimal import Decimal, InvalidOperation

from .models import Category, Brand, Product, Stock
from sales.models import Store

def parse_decimal(value, field_name):
    try:
        return Decimal(value)
    except (ValueError, InvalidOperation):
        raise ValueError(f"{field_name} phải là một số hợp lệ.")

def parse_int(value, field_name):
    try:
        return int(value)
    except (ValueError, TypeError):
        raise ValueError(f"{field_name} phải là một số nguyên hợp lệ.")

def get_object_or_404(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        raise

def error_response(message, status=400):
    return JsonResponse({'error': message}, status=status)

def success_response(data, status=200):
    return JsonResponse(data, status=status, safe=isinstance(data, dict))

@method_decorator(csrf_exempt, name='dispatch')
class ProductListView(View):
    """
    Xử lý GET để lấy danh sách sản phẩm với khả năng lọc và sắp xếp.
    Filters:
        - brand_id (int)
        - category_id (int)
        - min_price (decimal)
        - max_price (decimal)
    Sorting:
        - sort_by (string): 'product_name', 'list_price', 'model_year'
        - order_by (string): 'asc' (mặc định), 'desc'
    """
    def get(self, request):
        products = Product.objects.all()
        try:
            if brand_id := request.GET.get('brand_id'):
                products = products.filter(brand_id=parse_int(brand_id, 'brand_id'))
            if category_id := request.GET.get('category_id'):
                products = products.filter(category_id=parse_int(category_id, 'category_id'))
            if min_price := request.GET.get('min_price'):
                products = products.filter(list_price__gte=parse_decimal(min_price, 'min_price'))
            if max_price := request.GET.get('max_price'):
                products = products.filter(list_price__lte=parse_decimal(max_price, 'max_price'))
        except ValueError as e:
            return error_response(str(e))

        sort_by = request.GET.get('sort_by')
        order_by = request.GET.get('order_by', 'asc')
        valid_sort_fields = ['product_name', 'list_price', 'model_year']

        if sort_by:
            if sort_by not in valid_sort_fields:
                return error_response(
                    f'Trường sắp xếp không hợp lệ. Chỉ chấp nhận: {", ".join(valid_sort_fields)}'
                )
            sort_prefix = '-' if order_by == 'desc' else ''
            products = products.order_by(f'{sort_prefix}{sort_by}')

        product_data = [
            {
                'product_id': p.product_id,
                'product_name': p.product_name,
                'brand_name': p.brand_id.brand_name,
                'category_name': p.category_id.category_name,
                'model_year': p.model_year,
                'list_price': str(p.list_price)
            }
            for p in products
        ]
        return success_response(product_data)

    def post(self, request):
        """Tạo sản phẩm mới."""
        try:
            data = json.loads(request.body.decode('utf-8'))
            required_fields = ['product_id', 'product_name', 'brand_id', 'category_id', 'model_year', 'list_price']
            for field in required_fields:
                if field not in data:
                    return error_response(f'Thiếu trường bắt buộc: {field}')
            try:
                brand = get_object_or_404(Brand, brand_id=data['brand_id'])
            except Brand.DoesNotExist:
                return error_response(f"Brand với ID '{data['brand_id']}' không tồn tại.", 404)
            try:
                category = get_object_or_404(Category, category_id=data['category_id'])
            except Category.DoesNotExist:
                return error_response(f"Category với ID '{data['category_id']}' không tồn tại.", 404)
            try:
                new_product = Product.objects.create(
                    product_id=data['product_id'],
                    product_name=data['product_name'],
                    brand_id=brand,
                    category_id=category,
                    model_year=data['model_year'],
                    list_price=data['list_price']
                )
            except IntegrityError:
                return error_response(
                    f"Product với product_id '{data['product_id']}' đã tồn tại.", 409
                )
            response_data = {
                'message': 'Product created successfully',
                'product_id': new_product.product_id,
                'product_name': new_product.product_name,
                'brand_name': new_product.brand_id.brand_name,
                'category_name': new_product.category_id.category_name,
                'model_year': new_product.model_year,
                'list_price': str(new_product.list_price)
            }
            return success_response(response_data, 201)
        except json.JSONDecodeError:
            return error_response('Dữ liệu JSON không hợp lệ')
        except Exception as e:
            return error_response(f'Lỗi: {str(e)}', 500)

@method_decorator(csrf_exempt, name='dispatch')
class ProductDetailView(View):
    """
    Xử lý GET để lấy chi tiết sản phẩm, PATCH để cập nhật, DELETE để xóa.
    """
    def get(self, request, product_id):
        try:
            product = Product.objects.filter(product_id=product_id).first()
            if not product:
                return error_response('Sản phẩm không tồn tại', 404)
            product_detail = {
                'product_id': product.product_id,
                'product_name': product.product_name,
                'brand_name': product.brand_id.brand_name,
                'category_name': product.category_id.category_name,
                'model_year': product.model_year,
                'list_price': str(product.list_price),
            }
            return success_response(product_detail)
        except Exception as e:
            return error_response(f'Lỗi: {str(e)}', 500)

    def patch(self, request, product_id):
        try:
            try:
                product = Product.objects.get(product_id=product_id)
            except Product.DoesNotExist:
                return error_response('Sản phẩm không tồn tại', 404)
            data = json.loads(request.body.decode('utf-8'))
            updatable_fields = ['product_name', 'brand_id', 'category_id', 'model_year', 'list_price']
            has_changes = False
            for field in updatable_fields:
                if field in data:
                    if field == 'brand_id':
                        try:
                            new_brand = Brand.objects.get(brand_id=data[field])
                            if product.brand_id != new_brand:
                                product.brand_id = new_brand
                                has_changes = True
                        except Brand.DoesNotExist:
                            return error_response(f"Brand với ID '{data[field]}' không tồn tại.", 404)
                    elif field == 'category_id':
                        try:
                            new_category = Category.objects.get(category_id=data[field])
                            if product.category_id != new_category:
                                product.category_id = new_category
                                has_changes = True
                        except Category.DoesNotExist:
                            return error_response(f"Category với ID '{data[field]}' không tồn tại.", 404)
                    elif getattr(product, field) != data[field]:
                        setattr(product, field, data[field])
                        has_changes = True
            if not has_changes and not data:
                return success_response({
                    'product_id': product.product_id,
                    'product_name': product.product_name,
                    'brand_name': product.brand_id.brand_name,
                    'category_name': product.category_id.category_name,
                    'model_year': product.model_year,
                    'list_price': str(product.list_price)
                })
            product.save()
            updated_product_data = {
                'product_id': product.product_id,
                'product_name': product.product_name,
                'brand_name': product.brand_id.brand_name,
                'category_name': product.category_id.category_name,
                'model_year': product.model_year,
                'list_price': str(product.list_price)
            }
            return success_response(updated_product_data)
        except json.JSONDecodeError:
            return error_response('Dữ liệu JSON không hợp lệ')
        except ValidationError as e:
            return JsonResponse({'errors': e.message_dict}, status=400)
        except Exception as e:
            return error_response(f'Lỗi: {str(e)}', 500)

    def delete(self, request, product_id):
        try:
            try:
                product = Product.objects.get(product_id=product_id)
            except Product.DoesNotExist:
                return error_response('Sản phẩm không tồn tại', 404)
            product_name = product.product_name
            product.delete()
            return success_response(
                {'message': f'Sản phẩm {product_name} (ID: {product_id}) đã được xóa thành công.'}
            )
        except Exception as e:
            return error_response(f'Đã có lỗi xảy ra trong quá trình xóa: {str(e)}', 500)

@method_decorator(csrf_exempt, name='dispatch')
class StockListView(View):
    """
    Xử lý GET để lấy danh sách tồn kho và POST để thêm mới tồn kho.
    """
    def get(self, request):
        stocks = Stock.objects.all()
        stock_data = [
            {
                'store_id': s.store_id.store_id,
                'store_name': s.store_id.store_name,
                'product_id': s.product_id.product_id,
                'product_name': s.product_id.product_name,
                'quantity': s.quantity
            }
            for s in stocks
        ]
        return success_response(stock_data)

    def post(self, request):
        try:
            data = json.loads(request.body.decode('utf-8'))
            required_fields = ['store_id', 'product_id', 'quantity']
            for field in required_fields:
                if field not in data:
                    return error_response(f'Thiếu trường bắt buộc: {field}')
            try:
                store = get_object_or_404(Store, store_id=data['store_id'])
            except Store.DoesNotExist:
                return error_response(f"Cửa hàng với ID '{data['store_id']}' không tồn tại.", 404)
            try:
                product = get_object_or_404(Product, product_id=data['product_id'])
            except Product.DoesNotExist:
                return error_response(f"Sản phẩm với ID '{data['product_id']}' không tồn tại.", 404)
            if Stock.objects.filter(store_id=store, product_id=product).exists():
                return error_response(
                    'Bản ghi tồn kho cho sản phẩm này tại cửa hàng này đã tồn tại. Hãy dùng PATCH để cập nhật.', 409
                )
            new_stock = Stock.objects.create(
                store_id=store,
                product_id=product,
                quantity=data['quantity']
            )
            response_data = {
                'store_id': new_stock.store_id.store_id,
                'product_id': new_stock.product_id.product_id,
                'quantity': new_stock.quantity
            }
            return success_response(response_data, 201)
        except json.JSONDecodeError:
            return error_response('Dữ liệu JSON không hợp lệ')
        except IntegrityError as e:
            return error_response(f'Lỗi toàn vẹn dữ liệu: {str(e)}', 409)
        except Exception as e:
            return error_response(f'Lỗi: {str(e)}', 500)

@method_decorator(csrf_exempt, name='dispatch')
class StockDetailView(View):
    """
    Xử lý GET để lấy chi tiết tồn kho, PATCH để cập nhật, DELETE để xóa.
    Sử dụng cả store_id và product_id để định danh một bản ghi tồn kho.
    """
    def get(self, request, store_id, product_id):
        try:
            stock = Stock.objects.filter(store_id=store_id, product_id=product_id).first()
            if not stock:
                return error_response('Bản ghi tồn kho không tồn tại', 404)
            stock_detail = {
                'store_id': stock.store_id.store_id,
                'store_name': stock.store_id.store_name,
                'product_id': stock.product_id.product_id,
                'product_name': stock.product_id.product_name,
                'quantity': stock.quantity
            }
            return success_response(stock_detail)
        except Exception as e:
            return error_response(f'Lỗi: {str(e)}', 500)

    def patch(self, request, store_id, product_id):
        try:
            try:
                stock = Stock.objects.get(store_id=store_id, product_id=product_id)
            except Stock.DoesNotExist:
                return error_response('Bản ghi tồn kho không tồn tại', 404)
            data = json.loads(request.body.decode('utf-8'))
            if 'quantity' not in data:
                return error_response('Thiếu trường bắt buộc: quantity')
            new_quantity = data['quantity']
            if stock.quantity != new_quantity:
                stock.quantity = new_quantity
                stock.save()
                updated_stock_data = {
                    'store_id': stock.store_id.store_id,
                    'product_id': stock.product_id.product_id,
                    'quantity': stock.quantity
                }
                return success_response(updated_stock_data)
            else:
                return success_response({'message': 'Không có thay đổi nào được thực hiện.'})
        except json.JSONDecodeError:
            return error_response('Dữ liệu JSON không hợp lệ')
        except ValidationError as e:
            return JsonResponse({'errors': e.message_dict}, status=400)
        except Exception as e:
            return error_response(f'Lỗi: {str(e)}', 500)

    def delete(self, request, store_id, product_id):
        try:
            try:
                stock = Stock.objects.get(store_id=store_id, product_id=product_id)
            except Stock.DoesNotExist:
                return error_response('Bản ghi tồn kho không tồn tại', 404)
            stock.delete()
            return success_response(
                {'message': f'Bản ghi tồn kho cho sản phẩm ID {product_id} tại cửa hàng ID {store_id} đã được xóa thành công.'}
            )
        except Exception as e:
            return error_response(f'Đã có lỗi xảy ra trong quá trình xóa: {str(e)}', 500)