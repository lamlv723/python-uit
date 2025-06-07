from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError

from .models import Customer, Order, OrderItem, Staff, Store
from production.models import Product
import json
from functools import wraps

# ==== Utility Functions ====
def check_required_fields(data, required_fields):
    for field in required_fields:
        if field not in data:
            raise KeyError(f"Thiếu trường bắt buộc: {field}")

def update_instance_fields(instance, data, updatable_fields, fk_map=None):
    has_changes = False
    for field in updatable_fields:
        if field in data:
            value = data[field]
            # Nếu là ForeignKey, lấy instance
            if fk_map and field in fk_map and value is not None:
                model = fk_map[field]
                if value != getattr(instance, field + "_id", None):
                    value = model.objects.get(pk=value)
            if getattr(instance, field) != value:
                setattr(instance, field, value)
                has_changes = True
    return has_changes

def get_instance_or_404(model, pk, error_msg):
    try:
        return model.objects.get(pk=pk)
    except model.DoesNotExist:
        raise ValueError(error_msg)

def handle_exceptions(view_func):
    @wraps(view_func)
    def wrapper(self, request, *args, **kwargs):
        try:
            return view_func(self, request, *args, **kwargs)
        except KeyError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=404)
        except (Customer.DoesNotExist, Store.DoesNotExist, Staff.DoesNotExist, Order.DoesNotExist, Product.DoesNotExist, OrderItem.DoesNotExist):
            return JsonResponse({'error': 'Đối tượng không tồn tại'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Dữ liệu JSON không hợp lệ'}, status=400)
        except IntegrityError as e:
            return JsonResponse({'error': str(e)}, status=409)
        except ValidationError as e:
            return JsonResponse({'errors': e.message_dict}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Lỗi: {str(e)}'}, status=500)
    return wrapper

######################### CUSTOMER #########################
@method_decorator(csrf_exempt, name='dispatch')
class CustomerListView(View):
    @handle_exceptions
    def get(self, request):
        data = list(Customer.objects.all().values())
        return JsonResponse(data, safe=False)

    @handle_exceptions
    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        required_fields = ['customer_id', 'first_name', 'last_name', 'email']
        check_required_fields(data, required_fields)
        new_customer = Customer.objects.create(
            customer_id=data.get('customer_id'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            email=data.get('email'),
            phone=data.get('phone'),
            street=data.get('street'),
            city=data.get('city'),
            state=data.get('state'),
            zip_code=data.get('zip_code')
        )
        response_data = Customer.objects.filter(customer_id=new_customer.customer_id).values().first()
        return JsonResponse(response_data, status=201)

@method_decorator(csrf_exempt, name='dispatch')
class CustomerDetailView(View):
    @handle_exceptions
    def get(self, request, customer_id):
        customer_data = Customer.objects.filter(customer_id=customer_id).values().first()
        if customer_data:
            return JsonResponse(customer_data, safe=False)
        else:
            return JsonResponse({'error': 'Khách hàng không tồn tại'}, status=404)

    @handle_exceptions
    def patch(self, request, customer_id):
        customer = get_instance_or_404(Customer, customer_id, 'Khách hàng không tồn tại')
        data = json.loads(request.body.decode('utf-8'))
        updatable_fields = ['first_name', 'last_name', 'phone', 'email', 'street', 'city', 'state', 'zip_code']
        has_changes = update_instance_fields(customer, data, updatable_fields)
        if not has_changes and not data:
            current_data = Customer.objects.filter(customer_id=customer_id).values().first()
            return JsonResponse(current_data, status=200)
        customer.save()
        updated_customer_data = Customer.objects.filter(customer_id=customer.customer_id).values().first()
        return JsonResponse(updated_customer_data, status=200)

    @handle_exceptions
    def delete(self, request, customer_id):
        customer = get_instance_or_404(Customer, customer_id, 'Khách hàng không tồn tại')
        customer_name = f"{customer.first_name} {customer.last_name}"
        customer.delete()
        return JsonResponse({'message': f'Khách hàng {customer_name} (ID: {customer_id}) đã được xóa thành công.'}, status=200)

######################### ORDER #########################
@method_decorator(csrf_exempt, name='dispatch')
class OrderListView(View):
    @handle_exceptions
    def get(self, request):
        orders = list(Order.objects.all().values())
        return JsonResponse(orders, safe=False)

    @handle_exceptions
    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        required_fields = ['order_id', 'customer_id', 'order_status', 'order_date', 'store_id', 'staff_id']
        check_required_fields(data, required_fields)
        customer = get_instance_or_404(Customer, data.get('customer_id'), 'Customer không tồn tại')
        store = get_instance_or_404(Store, data.get('store_id'), 'Store không tồn tại')
        staff = get_instance_or_404(Staff, data.get('staff_id'), 'Staff không tồn tại')
        new_order = Order.objects.create(
            order_id=data.get('order_id'),
            customer_id=customer,
            order_status=data.get('order_status'),
            order_date=data.get('order_date'),
            required_date=data.get('required_date'),
            shipped_date=data.get('shipped_date'),
            store_id=store,
            staff_id=staff
        )
        response_data = Order.objects.filter(order_id=new_order.order_id).values().first()
        return JsonResponse(response_data, status=201)

@method_decorator(csrf_exempt, name='dispatch')
class OrderDetailView(View):
    @handle_exceptions
    def get(self, request, order_id):
        order = Order.objects.filter(order_id=order_id).values().first()
        if order:
            return JsonResponse(order, safe=False)
        else:
            return JsonResponse({'error': 'Đơn hàng không tồn tại'}, status=404)

    @handle_exceptions
    def patch(self, request, order_id):
        order = get_instance_or_404(Order, order_id, 'Đơn hàng không tồn tại')
        data = json.loads(request.body.decode('utf-8'))
        updatable_fields = ['customer_id', 'order_status', 'order_date', 'required_date', 'shipped_date', 'store_id', 'staff_id']
        fk_map = {
            'customer_id': Customer,
            'store_id': Store,
            'staff_id': Staff
        }
        has_changes = update_instance_fields(order, data, updatable_fields, fk_map)
        if not has_changes and not data:
            current_data = Order.objects.filter(order_id=order_id).values().first()
            return JsonResponse(current_data, status=200)
        order.save()
        updated_order = Order.objects.filter(order_id=order_id).values().first()
        return JsonResponse(updated_order, status=200)

    @handle_exceptions
    def delete(self, request, order_id):
        order = get_instance_or_404(Order, order_id, 'Đơn hàng không tồn tại')
        order.delete()
        return JsonResponse({'message': f'Đơn hàng {order_id} đã được xóa thành công.'}, status=200)

######################### ORDER ITEM #########################
@method_decorator(csrf_exempt, name='dispatch')
class OrderItemListView(View):
    @handle_exceptions
    def get(self, request):
        items = list(OrderItem.objects.all().values())
        return JsonResponse(items, safe=False)

    @handle_exceptions
    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        required_fields = ['order_id', 'item_id', 'product_id', 'quantity', 'list_price', 'discount']
        check_required_fields(data, required_fields)
        order = get_instance_or_404(Order, data.get('order_id'), 'Order không tồn tại')
        product = get_instance_or_404(Product, data.get('product_id'), 'Product không tồn tại')
        new_item = OrderItem.objects.create(
            order_id=order,
            item_id=data.get('item_id'),
            product_id=product,
            quantity=data.get('quantity'),
            list_price=data.get('list_price'),
            discount=data.get('discount')
        )
        response_data = OrderItem.objects.filter(order_id=new_item.order_id, item_id=new_item.item_id).values().first()
        return JsonResponse(response_data, status=201)

@method_decorator(csrf_exempt, name='dispatch')
class OrderItemDetailView(View):
    @handle_exceptions
    def get(self, request, order_id, item_id):
        item = OrderItem.objects.filter(order_id=order_id, item_id=item_id).values().first()
        if item:
            return JsonResponse(item, safe=False)
        else:
            return JsonResponse({'error': 'OrderItem không tồn tại'}, status=404)

    @handle_exceptions
    def patch(self, request, order_id, item_id):
        item = get_instance_or_404(OrderItem, {'order_id': order_id, 'item_id': item_id}, 'OrderItem không tồn tại')
        data = json.loads(request.body.decode('utf-8'))
        updatable_fields = ['product_id', 'quantity', 'list_price', 'discount']
        fk_map = {'product_id': Product}
        has_changes = update_instance_fields(item, data, updatable_fields, fk_map)
        if not has_changes and not data:
            current_data = OrderItem.objects.filter(order_id=order_id, item_id=item_id).values().first()
            return JsonResponse(current_data, status=200)
        item.save()
        updated_item = OrderItem.objects.filter(order_id=order_id, item_id=item_id).values().first()
        return JsonResponse(updated_item, status=200)

    @handle_exceptions
    def delete(self, request, order_id, item_id):
        item = get_instance_or_404(OrderItem, {'order_id': order_id, 'item_id': item_id}, 'OrderItem không tồn tại')
        item.delete()
        return JsonResponse({'message': f'OrderItem ({order_id}, {item_id}) đã được xóa thành công.'}, status=200)

######################### STAFF #########################
@method_decorator(csrf_exempt, name='dispatch')
class StaffListView(View):
    @handle_exceptions
    def get(self, request):
        staffs = list(Staff.objects.all().values())
        return JsonResponse(staffs, safe=False)

    @handle_exceptions
    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        required_fields = ['staff_id', 'first_name', 'last_name', 'email', 'store_id']
        check_required_fields(data, required_fields)
        store = get_instance_or_404(Store, data.get('store_id'), 'Store không tồn tại')
        manager = None
        if data.get('manager_id'):
            manager = get_instance_or_404(Staff, data.get('manager_id'), 'Manager không tồn tại')
        new_staff = Staff.objects.create(
            staff_id=data.get('staff_id'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            email=data.get('email'),
            phone=data.get('phone'),
            active=data.get('active', True),
            store_id=store,
            manager_id=manager
        )
        response_data = Staff.objects.filter(staff_id=new_staff.staff_id).values().first()
        return JsonResponse(response_data, status=201)

@method_decorator(csrf_exempt, name='dispatch')
class StaffDetailView(View):
    @handle_exceptions
    def get(self, request, staff_id):
        staff = Staff.objects.filter(staff_id=staff_id).values().first()
        if staff:
            return JsonResponse(staff, safe=False)
        else:
            return JsonResponse({'error': 'Nhân viên không tồn tại'}, status=404)

    @handle_exceptions
    def patch(self, request, staff_id):
        staff = get_instance_or_404(Staff, staff_id, 'Nhân viên không tồn tại')
        data = json.loads(request.body.decode('utf-8'))
        updatable_fields = ['first_name', 'last_name', 'email', 'phone', 'active', 'store_id', 'manager_id']
        fk_map = {'store_id': Store, 'manager_id': Staff}
        has_changes = update_instance_fields(staff, data, updatable_fields, fk_map)
        if not has_changes and not data:
            current_data = Staff.objects.filter(staff_id=staff_id).values().first()
            return JsonResponse(current_data, status=200)
        staff.save()
        updated_staff = Staff.objects.filter(staff_id=staff_id).values().first()
        return JsonResponse(updated_staff, status=200)

    @handle_exceptions
    def delete(self, request, staff_id):
        staff = get_instance_or_404(Staff, staff_id, 'Nhân viên không tồn tại')
        staff.delete()
        return JsonResponse({'message': f'Nhân viên {staff_id} đã được xóa thành công.'}, status=200)

######################### STORE #########################
@method_decorator(csrf_exempt, name='dispatch')
class StoreListView(View):
    @handle_exceptions
    def get(self, request):
        stores = list(Store.objects.all().values())
        return JsonResponse(stores, safe=False)

    @handle_exceptions
    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        required_fields = ['store_id', 'store_name', 'phone', 'email', 'street', 'city', 'state', 'zip_code']
        check_required_fields(data, required_fields)
        new_store = Store.objects.create(
            store_id=data.get('store_id'),
            store_name=data.get('store_name'),
            phone=data.get('phone'),
            email=data.get('email'),
            street=data.get('street'),
            city=data.get('city'),
            state=data.get('state'),
            zip_code=data.get('zip_code')
        )
        response_data = Store.objects.filter(store_id=new_store.store_id).values().first()
        return JsonResponse(response_data, status=201)

@method_decorator(csrf_exempt, name='dispatch')
class StoreDetailView(View):
    @handle_exceptions
    def get(self, request, store_id):
        store = Store.objects.filter(store_id=store_id).values().first()
        if store:
            return JsonResponse(store, safe=False)
        else:
            return JsonResponse({'error': 'Cửa hàng không tồn tại'}, status=404)

    @handle_exceptions
    def patch(self, request, store_id):
        store = get_instance_or_404(Store, store_id, 'Cửa hàng không tồn tại')
        data = json.loads(request.body.decode('utf-8'))
        updatable_fields = ['store_name', 'phone', 'email', 'street', 'city', 'state', 'zip_code']
        has_changes = update_instance_fields(store, data, updatable_fields)
        if not has_changes and not data:
            current_data = Store.objects.filter(store_id=store_id).values().first()
            return JsonResponse(current_data, status=200)
        store.save()
        updated_store = Store.objects.filter(store_id=store_id).values().first()
        return JsonResponse(updated_store, status=200)

    @handle_exceptions
    def delete(self, request, store_id):
        store = get_instance_or_404(Store, store_id, 'Cửa hàng không tồn tại')
        store.delete()
        return JsonResponse({'message': f'Cửa hàng {store_id} đã được xóa thành công.'}, status=200)