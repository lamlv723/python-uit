from django.shortcuts import render
from django.views import View
from django.http import HttpResponse, JsonResponse
from .models import Customer
import json

# Create your views here.

# Lam code
class CustomerListView(View):
    def get(self, request):
        # Lấy danh sách nhân viên
        customer_list = Customer.objects.all().values()

        data = list(customer_list)
        return JsonResponse(data, safe=False)
########################################################################