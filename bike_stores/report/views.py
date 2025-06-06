from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core.exceptions import ValidationError
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

import json
from . import utils
from .services import get_inventory_report_data

# Create your views here.
class InventoryReportView(View):
    # template_name = 'analytics_app/inventory_report.html' # Không cần template nữa

    def get(self, request, *args, **kwargs):
        inventory_data_grouped = get_inventory_report_data()

        report_title = "Báo cáo Tồn kho theo Cửa hàng và Sản phẩm"

        response_data = {
            'report_title': report_title,
            'data': inventory_data_grouped
        }

        return JsonResponse(response_data)