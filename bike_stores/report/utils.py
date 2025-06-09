from decimal import Decimal


def calculate_percentile_rank(sorted_revenues: list[Decimal], revenue_value: Decimal) -> float:
    """
    Tính xếp hạng phần trăm của một giá trị doanh thu trong một danh sách đã được sắp xếp.

    Args:
        sorted_revenues (list[Decimal]): Danh sách tất cả doanh thu, đã sắp xếp từ thấp đến cao.
        revenue_value (Decimal): Giá trị doanh thu của khách hàng cần tính.

    Returns:
        float: Xếp hạng phần trăm (từ 0 đến 100).
    """
    if not sorted_revenues:
        return 0.0

    count_lower = len([rev for rev in sorted_revenues if rev < revenue_value])

    count_equal = sorted_revenues.count(revenue_value)

    total_count = len(sorted_revenues)

    percentile = ((count_lower + 0.5 * count_equal) / total_count) * 100

    return percentile