from django.shortcuts import render
from django.views import View
from django.http import HttpResponse, JsonResponse
from jsonschema.exceptions import ValidationError

from .models import Customer
import json
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError


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
            # Nếu customer_id đã tồn tại, throw IntegrityError
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
            customer.full_clean()
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

######################### END #########################
