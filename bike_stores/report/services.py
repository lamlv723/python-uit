from production.models import Stock, Product
from sales.models import Store, OrderItem
from .utils import calculate_percentile_rank

from datetime import date, timedelta
from decimal import Decimal
from django.db import models
from django.db.models import functions as fn

import math

def get_inventory_report_data(store_id=None)->dict:
    """
    Lấy dữ liệu tồn kho theo từng sản phẩm theo cửa hàng
    """
    inventory_items = (
        Stock.objects
        .select_related('product_id', 'store_id')
        .order_by('store_id__store_name', 'product_id__product_name')
    )

    if store_id:
        inventory_items = inventory_items.filter(store_id=store_id)

    report_data_grouped = {}

    for item in inventory_items:
        store = item.store_id
        product = item.product_id

        store_name = getattr(store, 'store_name', 'Không xác định')
        product_id = getattr(product, 'product_id', None)
        product_name = getattr(product, 'product_name', 'Không xác định')

        if store_name not in report_data_grouped:
            report_data_grouped[store_name] = []

        report_data_grouped[store_name].append({
            'product_id': product_id,
            'product_name': product_name,
            'quantity': item.quantity,
        })

    return report_data_grouped


def get_revenue_report_data(end_date: date, start_date: date | None = None, period: str = 'month',
                            store_id: int | None = None) -> dict:
    """
    Lấy dữ liệu doanh thu, có thể lọc theo cửa hàng.
    """
    order_date_expr = models.Case(
        models.When(
            condition=models.Q(order_id__order_date__regex=r'^\d{8}$'),
            then=fn.Cast(
                fn.Concat(
                    fn.Substr(fn.Cast('order_id__order_date', output_field=models.CharField()), 1, 4),
                    models.Value('-'),
                    fn.Substr(fn.Cast('order_id__order_date', output_field=models.CharField()), 5, 2),
                    models.Value('-'),
                    fn.Substr(fn.Cast('order_id__order_date', output_field=models.CharField()), 7, 2)
                ),
                output_field=models.DateField()
            )
        ),
        default=fn.Cast('order_id__order_date', output_field=models.DateField()),
        output_field=models.DateField()
    )

    queryset = OrderItem.objects.annotate(casted_order_date=order_date_expr)
    queryset = queryset.exclude(casted_order_date__isnull=True)

    if store_id:
        queryset = queryset.filter(order_id__store_id=store_id)
        try:
            store_name = Store.objects.get(pk=store_id).store_name
        except Store.DoesNotExist:
            store_name = f"Không tìm thấy cửa hàng ID {store_id}"
    else:
        store_name = "Toàn hệ thống"

    actual_range = queryset.aggregate(
        first_date=models.Min('casted_order_date'),
        last_date=models.Max('casted_order_date')
    )
    if not actual_range['first_date']:
        return {'data': [], 'store_name': store_name}

    final_start_date = start_date if start_date else actual_range['first_date']
    final_end_date = min(end_date, actual_range['last_date'])
    if final_start_date > final_end_date:
        return {'data': [], 'store_name': store_name}

    date_filters = {'casted_order_date__range': [final_start_date, final_end_date]}
    time_trunc = {
        'day': fn.TruncDay('casted_order_date'), 'week': fn.TruncWeek('casted_order_date'),
        'month': fn.TruncMonth('casted_order_date'), 'quarter': fn.TruncQuarter('casted_order_date'),
        'year': fn.TruncYear('casted_order_date'),
    }.get(period, fn.TruncMonth('casted_order_date'))

    sales_data_from_db = (
        queryset.filter(**date_filters)
        .annotate(period=time_trunc).values('period')
        .annotate(total_revenue=models.Sum(
            models.F('quantity') * models.F('list_price') * (Decimal('1.0') - models.F('discount')),
            output_field=models.DecimalField()
        ))
    )

    sales_by_period = {
        item['period'].isoformat(): item['total_revenue'] for item in sales_data_from_db if item['period']
    }

    full_report_data = []
    current_date = final_start_date
    while current_date <= final_end_date:
        if period == 'day':
            period_start = current_date; current_date += timedelta(days=1)
        elif period == 'week':
            period_start = current_date - timedelta(days=current_date.weekday()); current_date += timedelta(weeks=1)
        elif period == 'month':
            period_start = date(current_date.year, current_date.month, 1)
            next_month = current_date.month + 1;
            next_year = current_date.year
            if next_month > 12: next_month = 1; next_year += 1
            current_date = date(next_year, next_month, 1)
        elif period == 'quarter':
            quarter = (current_date.month - 1) // 3 + 1
            period_start = date(current_date.year, 3 * quarter - 2, 1)
            current_date = period_start + timedelta(days=95);
            current_date = date(current_date.year, ((current_date.month - 1) // 3) * 3 + 1, 1)
        else:  # year
            period_start = date(current_date.year, 1, 1);
            current_date = date(current_date.year + 1, 1, 1)
        if period_start <= final_end_date and (not full_report_data or full_report_data[-1]['period'] != period_start):
            period_key = period_start.isoformat()
            revenue = sales_by_period.get(period_key, Decimal('0.0'))
            full_report_data.append({'period': period_start, 'total_revenue': revenue})

    return {'store_name': store_name, 'data': full_report_data}


def get_pareto_customer_analysis(end_date: date, start_date: date | None = None, store_id: int | None = None) -> dict:
    """
    Phân tích khách hàng theo nguyên lý Pareto, có thể lọc theo cửa hàng.
    Gán cờ is_8020 cho nhóm khách hàng top và trả về toàn bộ danh sách.
    """

    order_date_expr = models.Case(
        models.When(
            condition=models.Q(order_id__order_date__regex=r'^\d{8}$'),
            then=fn.Cast(
                fn.Concat(
                    fn.Substr(fn.Cast('order_id__order_date', output_field=models.CharField()), 1, 4),
                    models.Value('-'),
                    fn.Substr(fn.Cast('order_id__order_date', output_field=models.CharField()), 5, 2),
                    models.Value('-'),
                    fn.Substr(fn.Cast('order_id__order_date', output_field=models.CharField()), 7, 2)
                ),
                output_field=models.DateField()
            )
        ),
        default=fn.Cast('order_id__order_date', output_field=models.DateField()),
        output_field=models.DateField()
    )
    queryset = OrderItem.objects.annotate(casted_order_date=order_date_expr).exclude(casted_order_date__isnull=True)

    date_filters = {}
    if start_date: date_filters['casted_order_date__gte'] = start_date
    if end_date: date_filters['casted_order_date__lte'] = end_date
    if date_filters: queryset = queryset.filter(**date_filters)

    # Lọc theo store_id nếu được cung cấp
    if store_id:
        queryset = queryset.filter(order_id__store_id=store_id)
        try:
            store_name = Store.objects.get(pk=store_id).store_name
        except Store.DoesNotExist:
            store_name = f"Không tìm thấy cửa hàng ID {store_id}"
    else:
        store_name = "Toàn hệ thống"


    customer_revenues_qs = (
        queryset
        .values('order_id__customer_id', 'order_id__customer_id__first_name', 'order_id__customer_id__last_name',
                'order_id__customer_id__email')
        .annotate(customer_revenue=models.Sum(
            models.F('quantity') * models.F('list_price') * (Decimal('1.0') - models.F('discount'))
        ))
        .order_by('-customer_revenue')
    )

    customer_revenues_list = list(customer_revenues_qs)

    if not customer_revenues_list:
        return {'summary': 'Không có dữ liệu doanh thu phù hợp.', 'customers': [], 'store_name': store_name}


    total_customer_count = len(customer_revenues_list)
    top_20_percent_count = math.ceil(total_customer_count * 0.2)


    top_customer_ids = {c['order_id__customer_id'] for c in customer_revenues_list[:top_20_percent_count]}


    all_customers_result = []
    all_revenues_sorted = sorted([c['customer_revenue'] for c in customer_revenues_list])

    for rank, customer_data in enumerate(customer_revenues_list):
        customer_id = customer_data['order_id__customer_id']
        percentile = calculate_percentile_rank(all_revenues_sorted, customer_data['customer_revenue'])

        all_customers_result.append({
            "rank": rank + 1,
            "customer_id": customer_id,
            "full_name": f"{customer_data['order_id__customer_id__first_name']} {customer_data['order_id__customer_id__last_name']}",
            "email": customer_data['order_id__customer_id__email'],
            "revenue": customer_data['customer_revenue'],
            "percentile_rank": percentile,
            "is_8020": customer_id in top_customer_ids  # Gán cờ True/False
        })

    top_customers_group = customer_revenues_list[:top_20_percent_count]
    revenue_from_top_group = sum(c['customer_revenue'] for c in top_customers_group)
    grand_total_revenue = sum(c['customer_revenue'] for c in customer_revenues_list)
    percentage_revenue_from_top_group = (revenue_from_top_group / grand_total_revenue) * 100 if grand_total_revenue else 0

    summary = {
        "grand_total_revenue": grand_total_revenue,
        "total_customer_count": total_customer_count,
        "top_20_percent_group_summary": {
            "customer_count": top_20_percent_count,
            "revenue_generated": revenue_from_top_group,
            "percentage_of_total_revenue": percentage_revenue_from_top_group
        }
    }

    return {
        "store_name": store_name,
        "summary": summary,
        "customers": all_customers_result,
    }