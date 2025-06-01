from django.shortcuts import render
from django.views import View
from django.http import HttpResponse, JsonResponse
from .models import Customer
import json # Để xử lý dữ liệu JSON từ request body
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt # Để bỏ qua CSRF cho API (cẩn trọng khi dùng)
from django.db import IntegrityError # Để bắt lỗi khi customer_id đã tồn tại


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
                customer_id=data['customer_id'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data['email'],
                phone=data.get('phone'), # .get() để lấy giá trị nếu có, nếu không sẽ là None
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
            return JsonResponse({'error': f'Đã có lỗi xảy ra: {str(e)}'}, status=500)

######################### END #########################
