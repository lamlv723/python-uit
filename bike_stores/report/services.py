from production.models import Stock
from sales.models import Store


def get_inventory_report_data() -> dict:
    """
    Lấy dữ liệu tồn kho theo từng sản phẩm theo cửa hàng.
    Trả về dict với key là tên cửa hàng, value là list các sản phẩm và số lượng tồn kho.
    """
    inventory_items = (
        Stock.objects
        .select_related('product_id', 'store_id')
        .order_by('store_id__store_name', 'product_id__product_name')
    )

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