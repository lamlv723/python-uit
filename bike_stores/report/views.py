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
        store_id = request.GET.get('store_id')

        inventory_data_grouped = get_inventory_report_data(store_id=store_id)

        report_title = "Báo cáo tồn kho theo cừa hàng và sản phẩm"
        if store_id:
            report_title = f"Báo cáo tồn kho theo cừa hàng và sản phẩm (store_id: {store_id})"

        response_data = {
            'report_title': report_title,
            'data': inventory_data_grouped
        }

        return JsonResponse(response_data)