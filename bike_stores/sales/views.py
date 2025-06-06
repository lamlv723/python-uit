from django.shortcuts import render
from django.views import View
from django.http import HttpResponse, JsonResponse
from django.core.exceptions import ValidationError

from .models import Customer
import json
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from .models import Order, OrderItem, Staff, Store
from production.models import Product  


######################### START #########################
# Lam code
@method_decorator(csrf_exempt, name='dispatch') # Áp dụng csrf_exempt cho tất cả các method (GET, POST,...)
class CustomerListView(View):
    """Lấy danh sách khách hàng"""
    def get(self, request):
        customer_list = Customer.objects.all().values()
        # .values() trả về QuerySet các dicts, không phải là các đối tượng Customer đầy đủ
        # Nếu bạn muốn trả về các đối tượng Customer đầy đủ và sau đó serialize, cách làm sẽ khác
        # Nhưng với .values(), nó đã là list các dicts, phù hợp cho JsonResponse đơn giản.

        data = list(customer_list)
        return JsonResponse(data, safe=False)

    def post(self, request):
        """Tạo khách hàng mới"""
        try:
            # 1. Lấy dữ liệu JSON từ body của request
            # request.body chứa dữ liệu byte, cần decode thành string rồi parse JSON
            data = json.loads(request.body.decode('utf-8'))

            # 2. Kiểm tra các trường bắt buộc (ít nhất là customer_id, first_name, last_name, email)
            required_fields = ['customer_id', 'first_name', 'last_name', 'email']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({'error': f'Thiếu trường bắt buộc: {field}'}, status=400)

            # 3. Tạo đối tượng Customer mới
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

            # 4. Chuẩn bị dữ liệu trả về (thông tin khách hàng vừa tạo)
            response_data = {
                'customer_id': new_customer.customer_id,
                'first_name': new_customer.first_name,
                'last_name': new_customer.last_name,
                'email': new_customer.email,
                'phone': new_customer.phone,
                'street': new_customer.street,
                'city': new_customer.city,
                'state': new_customer.state,
                'zip_code': new_customer.zip_code,
            }
            return JsonResponse(response_data, status=201) # 201 Created

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Dữ liệu JSON không hợp lệ'}, status=400)
        except IntegrityError:
            # Lỗi nếu customer_id đã tồn tại (do là primary key)
            return JsonResponse(
                {'error': f"Customer với customer_id '{data.get('customer_id')}' đã tồn tại."}
                , status=409
            ) # 409 Conflict
        except Exception as e:
            # Bắt các lỗi không mong muốn khác
            return JsonResponse({'error': f'Lỗi: {str(e)}'}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class CustomerDetailView(View):
    def get(self, request, customer_id): # customer_id sẽ được truyền từ URL
        try:
            # Return dict hoặc None nếu không tìm thấy
            customer_data = Customer.objects.filter(customer_id=customer_id).values().first()

            if customer_data:
                return JsonResponse(customer_data, safe=False)
            else:
                return JsonResponse({'error': 'Khách hàng không tồn tại'}, status=404)
        except Exception as e:
            # Bắt các lỗi không mong muốn khác, ví dụ nếu customer_id không phải là số
            return JsonResponse({'error': f'Lỗi: {str(e)}'}, status=500)


    def patch(self, request, customer_id):
        try:
            # 1. Tìm khách hàng cần cập nhật
            try:
                customer = Customer.objects.get(customer_id=customer_id)
            except Customer.DoesNotExist:
                return JsonResponse({'error': 'Khách hàng không tồn tại'}, status=404)

            # 2. Lấy dữ liệu JSON từ body của request
            data = json.loads(request.body.decode('utf-8'))

            # 3. Cập nhật các trường của đối tượng customer
            # Không cho phép cập nhật customer_id (là primary key)
            updatable_fields = ['first_name', 'last_name', 'phone', 'email', 'street', 'city', 'state', 'zip_code']
            has_changes = False  # Flag để kiểm tra xem có thay đổi thực sự không

            for field in updatable_fields:
                if field in data:
                    # Chỉ cập nhật nếu giá trị mới khác giá trị cũ
                    if getattr(customer, field) != data[field]:
                        setattr(customer, field, data[field])
                        has_changes = True

            # Trả về thông tin hiện tại nếu không có gì để cập nhật
            if not has_changes and not data:
                current_data = Customer.objects.filter(customer_id=customer_id).values().first()
                return JsonResponse(current_data, status=200)

            # 4. Validate và Lưu thay đổi
            # full_clean() sẽ kiểm tra các ràng buộc của model (ví dụ: max_length)
            # customer.full_clean()
            customer.save()

            # 5. Chuẩn bị dữ liệu trả về (thông tin khách hàng vừa cập nhật)
            # Lấy lại dữ liệu từ DB để đảm bảo tính nhất quán (hoặc có thể tự xây dựng dict)
            updated_customer_data = Customer.objects.filter(customer_id=customer.customer_id).values().first()
            return JsonResponse(updated_customer_data, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Dữ liệu JSON không hợp lệ'}, status=400)
        except ValidationError as e:
            # e.message_dict chứa chi tiết lỗi validation cho từng trường
            return JsonResponse({'errors': e.message_dict}, status=400)
        except Exception as e:
            # Bắt các lỗi không mong muốn khác
            return JsonResponse({'error': f'Lỗi: {str(e)}'}, status=500)


    def delete(self, request, customer_id):
        try:
            # 1. Tìm khách hàng cần xóa
            try:
                customer = Customer.objects.get(customer_id=customer_id)
            except Customer.DoesNotExist:
                return JsonResponse({'error': 'Khách hàng không tồn tại'}, status=404)

            # 2. Thực hiện xóa
            # Order.customer_id có on_delete=models.CASCADE nên Order cũng sẽ bị xóa theo
            customer_name = f"{customer.first_name} {customer.last_name}"
            customer.delete()

            # 3. Trả về response thành công
            # return HttpResponse(status=204)
            return JsonResponse(
                {'message': f'Khách hàng {customer_name} (ID: {customer_id}) đã được xóa thành công.'},
                status=200)  # Hoặc 204 với HttpResponse(status=204)

        except Exception as e:
            # Bắt các lỗi không mong muốn khác
            return JsonResponse({'error': f'Đã có lỗi xảy ra trong quá trình xóa: {str(e)}'}, status=500)
######################### END #########################

@method_decorator(csrf_exempt, name='dispatch')
class OrderListView(View):
    def get(self, request):
        orders = list(Order.objects.all().values())
        return JsonResponse(orders, safe=False)

    def post(self, request):
        try:
            data = json.loads(request.body.decode('utf-8'))
            required_fields = ['order_id', 'customer_id', 'order_status', 'order_date', 'store_id', 'staff_id']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({'error': f'Thiếu trường bắt buộc: {field}'}, status=400)
            # Lấy instance cho các trường FK
            customer = Customer.objects.get(pk=data.get('customer_id'))
            store = Store.objects.get(pk=data.get('store_id'))
            staff = Staff.objects.get(pk=data.get('staff_id'))
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
        except Customer.DoesNotExist:
            return JsonResponse({'error': 'Customer không tồn tại'}, status=400)
        except Store.DoesNotExist:
            return JsonResponse({'error': 'Store không tồn tại'}, status=400)
        except Staff.DoesNotExist:
            return JsonResponse({'error': 'Staff không tồn tại'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Dữ liệu JSON không hợp lệ'}, status=400)
        except IntegrityError:
            return JsonResponse({'error': f"Order với order_id '{data.get('order_id')}' đã tồn tại."}, status=409)
        except Exception as e:
            return JsonResponse({'error': f'Lỗi: {str(e)}'}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class OrderDetailView(View):
    def get(self, request, order_id):
        try:
            order = Order.objects.filter(order_id=order_id).values().first()
            if order:
                return JsonResponse(order, safe=False)
            else:
                return JsonResponse({'error': 'Đơn hàng không tồn tại'}, status=404)
        except Exception as e:
            return JsonResponse({'error': f'Lỗi: {str(e)}'}, status=500)

    def patch(self, request, order_id):
        try:
            try:
                order = Order.objects.get(order_id=order_id)
            except Order.DoesNotExist:
                return JsonResponse({'error': 'Đơn hàng không tồn tại'}, status=404)
            data = json.loads(request.body.decode('utf-8'))
            updatable_fields = ['customer_id', 'order_status', 'order_date', 'required_date', 'shipped_date', 'store_id', 'staff_id']
            has_changes = False
            for field in updatable_fields:
                if field in data and getattr(order, field) != data[field]:
                    setattr(order, field, data[field])
                    has_changes = True
            if not has_changes and not data:
                current_data = Order.objects.filter(order_id=order_id).values().first()
                return JsonResponse(current_data, status=200)
            order.save()
            updated_order = Order.objects.filter(order_id=order_id).values().first()
            return JsonResponse(updated_order, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Dữ liệu JSON không hợp lệ'}, status=400)
        except ValidationError as e:
            return JsonResponse({'errors': e.message_dict}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Lỗi: {str(e)}'}, status=500)

    def delete(self, request, order_id):
        try:
            try:
                order = Order.objects.get(order_id=order_id)
            except Order.DoesNotExist:
                return JsonResponse({'error': 'Đơn hàng không tồn tại'}, status=404)
            order.delete()
            return JsonResponse({'message': f'Đơn hàng {order_id} đã được xóa thành công.'}, status=200)
        except Exception as e:
            return JsonResponse({'error': f'Đã có lỗi xảy ra trong quá trình xóa: {str(e)}'}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class OrderItemListView(View):
    def get(self, request):
        items = list(OrderItem.objects.all().values())
        return JsonResponse(items, safe=False)

    def post(self, request):
        try:
            data = json.loads(request.body.decode('utf-8'))
            required_fields = ['order_id', 'item_id', 'product_id', 'quantity', 'list_price', 'discount']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({'error': f'Thiếu trường bắt buộc: {field}'}, status=400)
            # Lấy instance cho các trường FK
            order = Order.objects.get(pk=data.get('order_id'))
            product = Product.objects.get(pk=data.get('product_id'))
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
        except Order.DoesNotExist:
            return JsonResponse({'error': 'Order không tồn tại'}, status=400)
        except Product.DoesNotExist:
            return JsonResponse({'error': 'Product không tồn tại'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Dữ liệu JSON không hợp lệ'}, status=400)
        except IntegrityError:
            return JsonResponse({'error': 'OrderItem đã tồn tại.'}, status=409)
        except Exception as e:
            return JsonResponse({'error': f'Lỗi: {str(e)}'}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class OrderItemDetailView(View):
    def get(self, request, order_id, item_id):
        try:
            item = OrderItem.objects.filter(order_id=order_id, item_id=item_id).values().first()
            if item:
                return JsonResponse(item, safe=False)
            else:
                return JsonResponse({'error': 'OrderItem không tồn tại'}, status=404)
        except Exception as e:
            return JsonResponse({'error': f'Lỗi: {str(e)}'}, status=500)

    def patch(self, request, order_id, item_id):
        try:
            try:
                item = OrderItem.objects.get(order_id=order_id, item_id=item_id)
            except OrderItem.DoesNotExist:
                return JsonResponse({'error': 'OrderItem không tồn tại'}, status=404)
            data = json.loads(request.body.decode('utf-8'))
            updatable_fields = ['product_id', 'quantity', 'list_price', 'discount']
            has_changes = False
            for field in updatable_fields:
                if field in data and getattr(item, field) != data[field]:
                    setattr(item, field, data[field])
                    has_changes = True
            if not has_changes and not data:
                current_data = OrderItem.objects.filter(order_id=order_id, item_id=item_id).values().first()
                return JsonResponse(current_data, status=200)
            item.save()
            updated_item = OrderItem.objects.filter(order_id=order_id, item_id=item_id).values().first()
            return JsonResponse(updated_item, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Dữ liệu JSON không hợp lệ'}, status=400)
        except ValidationError as e:
            return JsonResponse({'errors': e.message_dict}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Lỗi: {str(e)}'}, status=500)

    def delete(self, request, order_id, item_id):
        try:
            try:
                item = OrderItem.objects.get(order_id=order_id, item_id=item_id)
            except OrderItem.DoesNotExist:
                return JsonResponse({'error': 'OrderItem không tồn tại'}, status=404)
            item.delete()
            return JsonResponse({'message': f'OrderItem ({order_id}, {item_id}) đã được xóa thành công.'}, status=200)
        except Exception as e:
            return JsonResponse({'error': f'Đã có lỗi xảy ra trong quá trình xóa: {str(e)}'}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class StaffListView(View):
    def get(self, request):
        staffs = list(Staff.objects.all().values())
        return JsonResponse(staffs, safe=False)

    def post(self, request):
        try:
            data = json.loads(request.body.decode('utf-8'))
            required_fields = ['staff_id', 'first_name', 'last_name', 'email', 'store_id']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({'error': f'Thiếu trường bắt buộc: {field}'}, status=400)
            # Lấy instance cho ForeignKey
            store = Store.objects.get(pk=data.get('store_id'))
            manager = None
            if data.get('manager_id'):
                manager = Staff.objects.get(pk=data.get('manager_id'))
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
        except Store.DoesNotExist:
            return JsonResponse({'error': 'Store không tồn tại'}, status=400)
        except Staff.DoesNotExist:
            return JsonResponse({'error': 'Manager không tồn tại'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Dữ liệu JSON không hợp lệ'}, status=400)
        except IntegrityError:
            return JsonResponse({'error': f"Staff với staff_id '{data.get('staff_id')}' đã tồn tại."}, status=409)
        except Exception as e:
            return JsonResponse({'error': f'Lỗi: {str(e)}'}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class StaffDetailView(View):
    def get(self, request, staff_id):
        try:
            staff = Staff.objects.filter(staff_id=staff_id).values().first()
            if staff:
                return JsonResponse(staff, safe=False)
            else:
                return JsonResponse({'error': 'Nhân viên không tồn tại'}, status=404)
        except Exception as e:
            return JsonResponse({'error': f'Lỗi: {str(e)}'}, status=500)

    def patch(self, request, staff_id):
        try:
            try:
                staff = Staff.objects.get(staff_id=staff_id)
            except Staff.DoesNotExist:
                return JsonResponse({'error': 'Nhân viên không tồn tại'}, status=404)
            data = json.loads(request.body.decode('utf-8'))
            updatable_fields = ['first_name', 'last_name', 'email', 'phone', 'active', 'store_id', 'manager_id']
            has_changes = False
            for field in updatable_fields:
                if field in data and getattr(staff, field) != data[field]:
                    setattr(staff, field, data[field])
                    has_changes = True
            if not has_changes and not data:
                current_data = Staff.objects.filter(staff_id=staff_id).values().first()
                return JsonResponse(current_data, status=200)
            staff.save()
            updated_staff = Staff.objects.filter(staff_id=staff_id).values().first()
            return JsonResponse(updated_staff, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Dữ liệu JSON không hợp lệ'}, status=400)
        except ValidationError as e:
            return JsonResponse({'errors': e.message_dict}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Lỗi: {str(e)}'}, status=500)

    def delete(self, request, staff_id):
        try:
            try:
                staff = Staff.objects.get(staff_id=staff_id)
            except Staff.DoesNotExist:
                return JsonResponse({'error': 'Nhân viên không tồn tại'}, status=404)
            staff.delete()
            return JsonResponse({'message': f'Nhân viên {staff_id} đã được xóa thành công.'}, status=200)
        except Exception as e:
            return JsonResponse({'error': f'Đã có lỗi xảy ra trong quá trình xóa: {str(e)}'}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class StoreListView(View):
    def get(self, request):
        stores = list(Store.objects.all().values())
        return JsonResponse(stores, safe=False)

    def post(self, request):
        try:
            data = json.loads(request.body.decode('utf-8'))
            required_fields = ['store_id', 'store_name', 'phone', 'email', 'street', 'city', 'state', 'zip_code']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({'error': f'Thiếu trường bắt buộc: {field}'}, status=400)
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
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Dữ liệu JSON không hợp lệ'}, status=400)
        except IntegrityError:
            return JsonResponse({'error': f"Store với store_id '{data.get('store_id')}' đã tồn tại."}, status=409)
        except Exception as e:
            return JsonResponse({'error': f'Lỗi: {str(e)}'}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class StoreDetailView(View):
    def get(self, request, store_id):
        try:
            store = Store.objects.filter(store_id=store_id).values().first()
            if store:
                return JsonResponse(store, safe=False)
            else:
                return JsonResponse({'error': 'Cửa hàng không tồn tại'}, status=404)
        except Exception as e:
            return JsonResponse({'error': f'Lỗi: {str(e)}'}, status=500)

    def patch(self, request, store_id):
        try:
            try:
                store = Store.objects.get(store_id=store_id)
            except Store.DoesNotExist:
                return JsonResponse({'error': 'Cửa hàng không tồn tại'}, status=404)
            data = json.loads(request.body.decode('utf-8'))
            updatable_fields = ['store_name', 'phone', 'email', 'street', 'city', 'state', 'zip_code']
            has_changes = False
            for field in updatable_fields:
                if field in data and getattr(store, field) != data[field]:
                    setattr(store, field, data[field])
                    has_changes = True
            if not has_changes and not data:
                current_data = Store.objects.filter(store_id=store_id).values().first()
                return JsonResponse(current_data, status=200)
            store.save()
            updated_store = Store.objects.filter(store_id=store_id).values().first()
            return JsonResponse(updated_store, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Dữ liệu JSON không hợp lệ'}, status=400)
        except ValidationError as e:
            return JsonResponse({'errors': e.message_dict}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Lỗi: {str(e)}'}, status=500)

    def delete(self, request, store_id):
        try:
            try:
                store = Store.objects.get(store_id=store_id)
            except Store.DoesNotExist:
                return JsonResponse({'error': 'Cửa hàng không tồn tại'}, status=404)
            store.delete()
            return JsonResponse({'message': f'Cửa hàng {store_id} đã được xóa thành công.'}, status=200)
        except Exception as e:
            return JsonResponse({'error': f'Đã có lỗi xảy ra trong quá trình xóa: {str(e)}'}, status=500)