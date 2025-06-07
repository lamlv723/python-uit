from django.test import TestCase
from unittest.mock import MagicMock, patch

from .services import get_inventory_report_data

class GetInventoryReportDataTest(TestCase):
    @patch('report.services.Stock')
    def test_inventory_report_grouped_by_store(self, mock_stock):
        # Mock product and store objects
        mock_store1 = MagicMock(store_name='Store A')
        mock_store2 = MagicMock(store_name='Store B')
        mock_product1 = MagicMock(product_id=1, product_name='Bike 1')
        mock_product2 = MagicMock(product_id=2, product_name='Bike 2')

        # Mock Stock items
        mock_item1 = MagicMock(store_id=mock_store1, product_id=mock_product1, quantity=10)
        mock_item2 = MagicMock(store_id=mock_store1, product_id=mock_product2, quantity=5)
        mock_item3 = MagicMock(store_id=mock_store2, product_id=mock_product1, quantity=7)

        # Mock queryset
        mock_qs = [mock_item1, mock_item2, mock_item3]
        mock_stock.objects.select_related.return_value.order_by.return_value = mock_qs

        result = get_inventory_report_data()

        expected = {
            'Store A': [
                {'product_id': 1, 'product_name': 'Bike 1', 'quantity': 10},
                {'product_id': 2, 'product_name': 'Bike 2', 'quantity': 5},
            ],
            'Store B': [
                {'product_id': 1, 'product_name': 'Bike 1', 'quantity': 7},
            ]
        }
        self.assertEqual(result, expected)

    @patch('report.services.Stock')
    def test_inventory_report_with_missing_fields(self, mock_stock):
        # Store or product missing some fields
        mock_store = MagicMock()
        del mock_store.store_name
        mock_product = MagicMock()
        del mock_product.product_name
        del mock_product.product_id

        mock_item = MagicMock(store_id=mock_store, product_id=mock_product, quantity=3)
        mock_stock.objects.select_related.return_value.order_by.return_value = [mock_item]

        result = get_inventory_report_data()
        self.assertEqual(result, {
            'Không xác định': [
                {'product_id': None, 'product_name': 'Không xác định', 'quantity': 3}
            ]
        })