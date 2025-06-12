from django.views import View
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError, models
from decimal import Decimal, InvalidOperation
from .models import Category, Brand, Product, Stock
from sales.models import Store

import json

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

        brand_id = request.GET.get('brand_id')
        category_id = request.GET.get('category_id')
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')

        if brand_id:
            try:
                products = products.filter(brand_id=int(brand_id))
            except ValueError:
                return JsonResponse({'error': 'brand_id phải là một số nguyên hợp lệ.'}, status=400)
        
        if category_id:
            try:
                products = products.filter(category_id=int(category_id))
            except ValueError:
                return JsonResponse({'error': 'category_id phải là một số nguyên hợp lệ.'}, status=400)
        
        if min_price:
            try:
                products = products.filter(list_price__gte=Decimal(min_price))
            except InvalidOperation:
                return JsonResponse({'error': 'min_price phải là một số hợp lệ.'}, status=400)
        
        if max_price:
            try:
                products = products.filter(list_price__lte=Decimal(max_price))
            except InvalidOperation:
                return JsonResponse({'error': 'max_price phải là một số hợp lệ.'}, status=400)

        sort_by = request.GET.get('sort_by')
        order_by = request.GET.get('order_by', 'asc')
        valid_sort_fields = ['product_name', 'list_price', 'model_year']

        if sort_by and sort_by in valid_sort_fields:
            if order_by == 'desc':
                products = products.order_by(f'-{sort_by}')
            else:
                products = products.order_by(sort_by)
        elif sort_by and sort_by not in valid_sort_fields:
            return JsonResponse({'error': f'Trường sắp xếp không hợp lệ. Chỉ chấp nhận: {", ".join(valid_sort_fields)}'}, status=400)

        product_data = []
        for product in products:
            product_data.append({
                'product_id': product.product_id,
                'product_name': product.product_name,
                'brand_name': product.brand_id.brand_name,
                'category_name': product.category_id.category_name,
                'model_year': product.model_year,
                'list_price': str(product.list_price)
            })
        return JsonResponse(product_data, safe=False)

    def post(self, request):
        """Tạo sản phẩm mới."""
        try:
            data = json.loads(request.body.decode('utf-8'))

            required_fields = ['product_id', 'product_name', 'brand_id', 'category_id', 'model_year', 'list_price']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({'error': f'Thiếu trường bắt buộc: {field}'}, status=400)

            try:
                brand = Brand.objects.get(brand_id=data.get('brand_id'))
            except Brand.DoesNotExist:
                return JsonResponse({'error': f"Brand với ID '{data.get('brand_id')}' không tồn tại."}, status=404)

            try:
                category = Category.objects.get(category_id=data.get('category_id'))
            except Category.DoesNotExist:
                return JsonResponse({'error': f"Category với ID '{data.get('category_id')}' không tồn tại."}, status=404)

            new_product = Product.objects.create(
                product_id=data.get('product_id'),
                product_name=data.get('product_name'),
                brand_id=brand,
                category_id=category,
                model_year=data.get('model_year'),
                list_price=data.get('list_price')
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
            return JsonResponse(response_data, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Dữ liệu JSON không hợp lệ'}, status=400)
        except IntegrityError:
            return JsonResponse(
                {'error': f"Product với product_id '{data.get('product_id')}' đã tồn tại."}
                , status=409
            )
        except Exception as e:
            return JsonResponse({'error': f'Lỗi: {str(e)}'}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class ProductDetailView(View):
    def get(self, request, product_id):
        try:
            product = Product.objects.filter(product_id=product_id).first()
            if product:
                product_detail = {
                    'product_id': product.product_id,
                    'product_name': product.product_name,
                    'brand_name': product.brand_id.brand_name,
                    'category_name': product.category_id.category_name,
                    'model_year': product.model_year,
                    'list_price': str(product.list_price),
                }
                return JsonResponse(product_detail)
            else:
                return JsonResponse({'error': 'Sản phẩm không tồn tại'}, status=404)
        except Exception as e:
            return JsonResponse({'error': f'Lỗi: {str(e)}'}, status=500)
    
    def patch(self, request, product_id):
        try:
            try:
                product = Product.objects.get(product_id=product_id)
            except Product.DoesNotExist:
                return JsonResponse({'error': 'Sản phẩm không tồn tại'}, status=404)

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
                            return JsonResponse({'error': f"Brand với ID '{data[field]}' không tồn tại."}, status=404)
                    elif field == 'category_id':
                        try:
                            new_category = Category.objects.get(category_id=data[field])
                            if product.category_id != new_category:
                                product.category_id = new_category
                                has_changes = True
                        except Category.DoesNotExist:
                            return JsonResponse({'error': f"Category với ID '{data[field]}' không tồn tại."}, status=404)
                    elif getattr(product, field) != data[field]:
                        setattr(product, field, data[field])
                        has_changes = True

            if not has_changes and not data:
                return JsonResponse({
                    'product_id': product.product_id,
                    'product_name': product.product_name,
                    'brand_name': product.brand_id.brand_name,
                    'category_name': product.category_id.category_name,
                    'model_year': product.model_year,
                    'list_price': str(product.list_price)
                }, status=200)

            product.save()

            updated_product_data = {
                'product_id': product.product_id,
                'product_name': product.product_name,
                'brand_name': product.brand_id.brand_name,
                'category_name': product.category_id.category_name,
                'model_year': product.model_year,
                'list_price': str(product.list_price)
            }
            return JsonResponse(updated_product_data, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Dữ liệu JSON không hợp lệ'}, status=400)
        except ValidationError as e:
            return JsonResponse({'errors': e.message_dict}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Lỗi: {str(e)}'}, status=500)

    def delete(self, request, product_id):
        try:
            try:
                product = Product.objects.get(product_id=product_id)
            except Product.DoesNotExist:
                return JsonResponse({'error': 'Sản phẩm không tồn tại'}, status=404)

            product_name = product.product_name
            product.delete()

            return JsonResponse(
                {'message': f'Sản phẩm {product_name} (ID: {product_id}) đã được xóa thành công.'},
                status=200)

        except Exception as e:
            return JsonResponse({'error': f'Đã có lỗi xảy ra trong quá trình xóa: {str(e)}'}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class StockListView(View):
    def get(self, request):
        stocks = Stock.objects.all()
        stock_data = []
        for stock in stocks:
            stock_data.append({
                'store_id': stock.store_id.store_id,
                'store_name': stock.store_id.store_name,
                'product_id': stock.product_id.product_id,
                'product_name': stock.product_id.product_name,
                'quantity': stock.quantity
            })
        return JsonResponse(stock_data, safe=False)

    def post(self, request):
        try:
            data = json.loads(request.body.decode('utf-8'))

            required_fields = ['store_id', 'product_id', 'quantity']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({'error': f'Thiếu trường bắt buộc: {field}'}, status=400)

            try:
                store = Store.objects.get(store_id=data.get('store_id'))
            except Store.DoesNotExist:
                return JsonResponse({'error': f"Cửa hàng với ID '{data.get('store_id')}' không tồn tại."}, status=404)

            try:
                product = Product.objects.get(product_id=data.get('product_id'))
            except Product.DoesNotExist:
                return JsonResponse({'error': f"Sản phẩm với ID '{data.get('product_id')}' không tồn tại."}, status=404)

            if Stock.objects.filter(store_id=store, product_id=product).exists():
                return JsonResponse({'error': 'Bản ghi tồn kho cho sản phẩm này tại cửa hàng này đã tồn tại. Hãy dùng PATCH để cập nhật.'}, status=409)

            new_stock = Stock.objects.create(
                store_id=store,
                product_id=product,
                quantity=data.get('quantity')
            )

            response_data = {
                'store_id': new_stock.store_id.store_id,
                'product_id': new_stock.product_id.product_id,
                'quantity': new_stock.quantity
            }
            return JsonResponse(response_data, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Dữ liệu JSON không hợp lệ'}, status=400)
        except IntegrityError as e:
            return JsonResponse({'error': f'Lỗi toàn vẹn dữ liệu: {str(e)}'}, status=409)
        except Exception as e:
            return JsonResponse({'error': f'Lỗi: {str(e)}'}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class StockDetailView(View):
    def get(self, request, store_id, product_id):
        try:
            stock = Stock.objects.filter(store_id=store_id, product_id=product_id).first()
            if stock:
                stock_detail = {
                    'store_id': stock.store_id.store_id,
                    'store_name': stock.store_id.store_name,
                    'product_id': stock.product_id.product_id,
                    'product_name': stock.product_id.product_name,
                    'quantity': stock.quantity
                }
                return JsonResponse(stock_detail)
            else:
                return JsonResponse({'error': 'Bản ghi tồn kho không tồn tại'}, status=404)
        except Exception as e:
            return JsonResponse({'error': f'Lỗi: {str(e)}'}, status=500)

    def patch(self, request, store_id, product_id):
        try:
            try:
                stock = Stock.objects.get(store_id=store_id, product_id=product_id)
            except Stock.DoesNotExist:
                return JsonResponse({'error': 'Bản ghi tồn kho không tồn tại'}, status=404)

            data = json.loads(request.body.decode('utf-8'))

            if 'quantity' not in data:
                return JsonResponse({'error': 'Thiếu trường bắt buộc: quantity'}, status=400)

            new_quantity = data.get('quantity')
            if stock.quantity != new_quantity:
                stock.quantity = new_quantity
                stock.save()
                updated_stock_data = {
                    'store_id': stock.store_id.store_id,
                    'product_id': stock.product_id.product_id,
                    'quantity': stock.quantity
                }
                return JsonResponse(updated_stock_data, status=200)
            else:
                return JsonResponse({'message': 'Không có thay đổi nào được thực hiện.'}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Dữ liệu JSON không hợp lệ'}, status=400)
        except ValidationError as e:
            return JsonResponse({'errors': e.message_dict}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Lỗi: {str(e)}'}, status=500)

    def delete(self, request, store_id, product_id):
        try:
            try:
                stock = Stock.objects.get(store_id=store_id, product_id=product_id)
            except Stock.DoesNotExist:
                return JsonResponse({'error': 'Bản ghi tồn kho không tồn tại'}, status=404)

            stock.delete()

            return JsonResponse(
                {'message': f'Bản ghi tồn kho cho sản phẩm ID {product_id} tại cửa hàng ID {store_id} đã được xóa thành công.'},
                status=200)

        except Exception as e:
            return JsonResponse({'error': f'Đã có lỗi xảy ra trong quá trình xóa: {str(e)}'}, status=500)