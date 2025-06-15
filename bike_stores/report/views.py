from datetime import date
from django.shortcuts import render
from django.http import JsonResponse
from django.views import View

from .services import (
    get_inventory_report_data
    , get_revenue_report_data
    , get_pareto_customer_analysis
)


# Inventory report
class InventoryReportView(View):
    # template_name = 'analytics_app/inventory_report.html'

    def get(self, request, *args, **kwargs):
        store_id = request.GET.get('store_id')

        inventory_data_grouped = get_inventory_report_data(store_id=store_id)

        report_title = "Báo cáo hàng tồn kho"
        if store_id:
            report_title = f"Báo cáo hàng tồn kho (store_id: {store_id})"

        response_data = {
            'report_title': report_title,
            'data': inventory_data_grouped
        }

        return JsonResponse(response_data)


# Revenue report
class RevenueReportView(View):
    """
    Báo cáo doanh thu theo thời gian.
    """

    def get(self, request, *args, **kwargs):
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date', date.today().isoformat())
        period = request.GET.get('period', 'month')
        store_id_str = request.GET.get('store_id')

        if period not in ['day', 'week', 'month', 'quarter', 'year']:
            return JsonResponse(
                {'error': "Tham số 'period' phải là 'day', 'week', 'month', 'quarter', hoặc 'year'."},
                status=400
            )

        try:
            end_date = date.fromisoformat(end_date_str)
            start_date = date.fromisoformat(start_date_str) if start_date_str else None
            store_id = int(store_id_str) if store_id_str else None
        except (ValueError, TypeError):
            return JsonResponse({'error': "Định dạng tham số không hợp lệ (ngày tháng, store_id)."}, status=400)

        revenue_result = get_revenue_report_data(
            start_date=start_date,
            end_date=end_date,
            period=period,
            store_id=store_id
        )

        # sales_data = revenue_result.get('data', [])
        # store_name = revenue_result.get('store_name', 'Lỗi không xác định')

        # Format response
        if revenue_result.get('data'):
            for item in revenue_result.get('data'):
                item['period'] = item['period'].strftime("%Y-%m-%d")
                item['total_revenue'] = f"{item['total_revenue']:,.2f}"

        response_data = {
            'report_title': 'Báo cáo Doanh thu theo Thời gian',
            # 'store_name': store_name,
            'currency': 'VND',
            'query_params': {
                'start_date': start_date_str, 'end_date': end_date_str,
                'period': period, 'store_id': store_id
            },
            'revenue': revenue_result
        }
        return JsonResponse(response_data)


# Customer analysis - Patero
class CustomerAnalysisView(View):
    def get(self, request, *args, **kwargs):
        # Lấy các tham số từ URL
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date', date.today().isoformat())
        store_id_str = request.GET.get('store_id')
        limit_str = request.GET.get('limit')

        # Validate và chuyển đổi kiểu dữ liệu
        try:
            end_date = date.fromisoformat(end_date_str)
            start_date = date.fromisoformat(start_date_str) if start_date_str else None
            store_id = int(store_id_str) if store_id_str else None
            limit = int(limit_str) if limit_str else None
        except (ValueError, TypeError):
            return JsonResponse(
                {'error': "Định dạng tham số không hợp lệ (ngày tháng, store_id, limit)."},
                status=400
            )

        # Gọi service để lấy toàn bộ dữ liệu phân tích
        analysis_data = get_pareto_customer_analysis(start_date=start_date, end_date=end_date, store_id=store_id)

        # Lấy danh sách khách hàng đầy đủ từ kết quả phân tích
        all_customers = analysis_data.get('customers', [])

        # Xử lý hiển thị danh sách khách hàng
        if limit is not None:
            # Nếu người dùng cung cấp limit, lấy đúng số lượng đó từ đầu danh sách
            customers_to_display = all_customers[:limit]
        else:
            # Mặc định: Nếu không có limit, chỉ lọc ra những khách hàng thuộc nhóm top 20%
            customers_to_display = [
                customer for customer in all_customers if customer.get('is_8020') is True
            ]

        # Cập nhật lại danh sách khách hàng trong kết quả cuối cùng
        analysis_data['customers'] = customers_to_display

        # Định dạng lại các số để hiển thị đẹp hơn (phần này có thể tùy chỉnh)
        summary = analysis_data.get('summary', {})
        if isinstance(summary, dict):
            summary['grand_total_revenue'] = f"{summary.get('grand_total_revenue', 0):,.2f}"
            if 'top_20_percent_group_summary' in summary:
                group_summary = summary['top_20_percent_group_summary']
                group_summary['revenue_generated'] = f"{group_summary.get('revenue_generated', 0):,.2f}"
                group_summary[
                    'percentage_of_total_revenue'] = f"{group_summary.get('percentage_of_total_revenue', 0):.2f}%"

        for customer in analysis_data['customers']:
            customer['revenue'] = f"{customer.get('revenue', 0):,.2f}"
            customer['percentile_rank'] = f"{customer.get('percentile_rank', 0):.2f}"

        response_data = {
            'report_title': f"Phân tích khách hàng ({analysis_data.get('store_name')})",
            'query_params': {
                'start_date': start_date_str, 'end_date': end_date_str,
                'store_id': store_id, 'limit': limit,
            },
            'analysis': analysis_data
        }

        return JsonResponse(response_data)