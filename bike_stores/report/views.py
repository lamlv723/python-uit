from datetime import date
from django.shortcuts import render
from django.http import JsonResponse
from django.views import View

from .services import (
    get_inventory_report_data
    , get_sales_over_time_data
    , get_pareto_customer_analysis
)


# Create your views here.
class InventoryReportView(View):
    # template_name = 'analytics_app/inventory_report.html'

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


class RevenueOverTimeReportView(View):
    """
    API trả về báo cáo doanh thu theo thời gian.
    Có thể lọc theo start_date, end_date và nhóm theo period.
    """

    def get(self, request, *args, **kwargs):
        # Lấy tham số từ URL, nếu không có thì đặt giá trị mặc định/None
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date', date.today().isoformat())
        period = request.GET.get('period', 'month')

        # Validate tham số period
        if period not in ['day', 'week', 'month', 'quarter', 'year']:
            return JsonResponse(
                {'error': "Tham số 'period' phải là 'day', 'week', 'month', 'quarter', hoặc 'year'."},
                status=400
            )

        # Chuyển đổi string thành object date
        try:
            end_date = date.fromisoformat(end_date_str)
            start_date = date.fromisoformat(start_date_str) if start_date_str else None
        except ValueError:
            return JsonResponse(
                {'error': "Định dạng ngày không hợp lệ. Vui lòng dùng YYYY-MM-DD."},
                status=400
            )

        # Gọi hàm service để lấy dữ liệu
        sales_data = get_sales_over_time_data(start_date=start_date, end_date=end_date, period=period)

        # Format lại dữ liệu để đảm bảo an toàn khi parse JSON phía client
        formatted_data = [
            {
                'period': item['period'].strftime('%Y-%m-%d'),
                'total_revenue': f"{item['total_revenue']:.3f}"
            }
            for item in sales_data
        ]

        response_data = {
            'report_title': 'Báo cáo Doanh thu theo Thời gian',
            'currency': 'VND',
            'query_params': {
                'start_date': start_date_str,
                'end_date': end_date_str,
                'period': period,
            },
            'data': formatted_data
        }

        return JsonResponse(response_data)


class ParetoCustomerReportView(View):
    def get(self, request, *args, **kwargs):
        # ... logic lấy start_date, end_date giữ nguyên ...
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date', date.today().isoformat())
        try:
            end_date = date.fromisoformat(end_date_str)
            start_date = date.fromisoformat(start_date_str) if start_date_str else None
        except ValueError:
            return JsonResponse({'error': "Định dạng ngày không hợp lệ..."}, status=400)

        analysis_data = get_pareto_customer_analysis(start_date=start_date, end_date=end_date)

        # Định dạng lại các số để hiển thị đẹp hơn
        summary = analysis_data.get('summary', {})
        if isinstance(summary, dict):
             summary['grand_total_revenue'] = f"{summary.get('grand_total_revenue', 0):.2f}"
             if 'top_20_percent_group_summary' in summary:
                 group_summary = summary['top_20_percent_group_summary']
                 group_summary['revenue_generated'] = f"{group_summary.get('revenue_generated', 0):.2f}"
                 group_summary['percentage_of_total_revenue'] = f"{group_summary.get('percentage_of_total_revenue', 0):.2f}%"

        top_customers = analysis_data.get('top_customers', [])
        for customer in top_customers:
            customer['revenue'] = f"{customer.get('revenue', 0):.2f}"
            customer['percentile_rank'] = f"{customer.get('percentile_rank', 0):.2f}"

        response_data = {
            'report_title': f"Phân tích khách hàng",
            'query_params': {'start_date': start_date_str, 'end_date': end_date_str},
            'analysis': analysis_data
        }

        return JsonResponse(response_data)