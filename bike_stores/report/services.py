from production.models import Stock, Product
from sales.models import Store


def get_inventory_report_data()->dict:
    """
    Lấy dữ liệu tồn kho theo từng sản phẩm theo cửa hàng
    """

    inventory_items = (Stock.objects
                       .select_related('products', 'stores')
                       .order_by('store_name', 'product_name')
                    )

    report_data_grouped = {}
    for item in inventory_items:
        store_name = item.store.store_name if item.store else "Không xác định"

        product_name = item.product.product_name if item.product else "Không xác định"

        if store_name not in report_data_grouped:
            report_data_grouped[store_name] = []

        report_data_grouped[store_name].append({
            'product_id': item.product.product_id if item.product else None,
            'product_name': product_name,
            'quantity': item.quantity,
            # 'last_updated': item.last_updated # Nếu model Stock của bạn có trường này
        })
    print(inventory_items)
    return report_data_grouped

if __name__ == '__main__':
    get_inventory_report_data()