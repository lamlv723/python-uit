from production.models import Stock, Product
from sales.models import Store


def get_inventory_report_data()->dict:
    """
    Lấy dữ liệu tồn kho theo từng sản phẩm theo cửa hàng
    """
    inventory_items = (Stock.objects
                       .select_related('product_id', 'store_id')
                       .order_by('store_id__store_name', 'product_id__product_name')
                    )

    report_data_grouped = {}
    for item in inventory_items:
        store_name = item.store_id.store_name if item.store_id else "Không xác định"

        product_name = item.product_id.product_name if item.product_id else "Không xác định"

        if store_name not in report_data_grouped:
            report_data_grouped[store_name] = []

        report_data_grouped[store_name].append({
            'product_id': item.product_id.product_id if item.product_id else None,
            'product_name': product_name,
            'quantity': item.quantity,
        })
    print(inventory_items)
    return report_data_grouped
