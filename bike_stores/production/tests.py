from django.test import TestCase, Client
from django.urls import reverse
import json
from decimal import Decimal
from production.models import Category, Brand, Product, Stock
from sales.models import Store

class ProductionAPITests(TestCase):
    """
    Tests for Product and Stock APIs in the production app.
    Data is loaded from a Django fixture generated from load_data_modified.sql.
    Includes tests for filtering and sorting products.
    """
    fixtures = ['production_initial_data']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()
        # Brands
        cls.brand_electra = Brand.objects.get(brand_id=1)
        cls.brand_haro = Brand.objects.get(brand_id=2)
        cls.brand_heller = Brand.objects.get(brand_id=3)
        cls.brand_purecycles = Brand.objects.get(brand_id=4)
        cls.brand_ritchey = Brand.objects.get(brand_id=5)
        cls.brand_sun_bicycles = Brand.objects.get(brand_id=7)
        cls.brand_surly = Brand.objects.get(brand_id=8)
        cls.brand_trek = Brand.objects.get(brand_id=9)
        # Categories
        cls.category_children = Category.objects.get(category_id=1)
        cls.category_comfort = Category.objects.get(category_id=2)
        cls.category_cruisers = Category.objects.get(category_id=3)
        cls.category_cyclocross = Category.objects.get(category_id=4)
        cls.category_electric = Category.objects.get(category_id=5)
        cls.category_mountain = Category.objects.get(category_id=6)
        cls.category_road = Category.objects.get(category_id=7)
        # Stores
        cls.store_santa_cruz = Store.objects.get(store_id=1)
        cls.store_baldwin = Store.objects.get(store_id=2)
        cls.store_rowlett = Store.objects.get(store_id=3)
        # Products (some samples)
        cls.product_trek_820 = Product.objects.get(product_id=1)
        cls.product_ritchey = Product.objects.get(product_id=2)
        cls.product_surly_wednesday = Product.objects.get(product_id=3)
        cls.product_trek_fuel_ex8 = Product.objects.get(product_id=4)
        cls.product_heller_shagamaw = Product.objects.get(product_id=5)
        cls.product_surly_ice_cream = Product.objects.get(product_id=6)
        cls.product_trek_slash8 = Product.objects.get(product_id=7)
        cls.product_trek_remedy29 = Product.objects.get(product_id=8)
        cls.product_trek_conduit = Product.objects.get(product_id=9)
        cls.product_surly_straggler = Product.objects.get(product_id=10)
        # Stocks
        cls.stock_trek_820_santa_cruz = Stock.objects.get(store_id=cls.store_santa_cruz, product_id=cls.product_trek_820)
        cls.stock_ritchey_santa_cruz = Stock.objects.get(store_id=cls.store_santa_cruz, product_id=cls.product_ritchey)

    # --- Helper methods ---
    def _get_product_ids(self, data):
        return [item['product_id'] for item in data]

    def _assert_sorted(self, data, key, reverse=False):
        values = [item[key] for item in data]
        self.assertEqual(values, sorted(values, reverse=reverse))

    def _assert_all(self, data, key, value):
        for item in data:
            self.assertEqual(item[key], value)

    def _assert_price_range(self, data, min_price=None, max_price=None):
        for item in data:
            price = Decimal(item['list_price'])
            if min_price is not None:
                self.assertGreaterEqual(price, Decimal(str(min_price)))
            if max_price is not None:
                self.assertLessEqual(price, Decimal(str(max_price)))

    # --- Product API: Filter, Sort, Combine ---
    def test_product_filter_sort_and_combine(self):
        # Filter by brand
        response = self.client.get(reverse('product-list-create') + '?brand_id=9')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self._assert_all(data, 'brand_name', 'Trek')

        # Filter by category
        response = self.client.get(reverse('product-list-create') + '?category_id=6')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self._assert_all(data, 'category_name', 'Mountain Bikes')

        # Filter by price range
        response = self.client.get(reverse('product-list-create') + '?min_price=500&max_price=1000')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self._assert_price_range(data, 500, 1000)

        # Filter by non-existent brand/category
        for param in ['brand_id=99999', 'category_id=99999']:
            with self.subTest(param=param):
                response = self.client.get(reverse('product-list-create') + f'?{param}')
                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(response.json()), 0)

        # Filter by invalid brand/category
        for param, msg in [('brand_id=abc', 'brand_id phải là một số nguyên hợp lệ.'),
                           ('category_id=xyz', 'category_id phải là một số nguyên hợp lệ.')]:
            with self.subTest(param=param):
                response = self.client.get(reverse('product-list-create') + f'?{param}')
                self.assertEqual(response.status_code, 400)
                self.assertIn(msg, response.json()['error'])

        # Filter by invalid price
        for param, msg in [('min_price=invalid', 'min_price phải là một số hợp lệ.'),
                           ('max_price=invalid', 'max_price phải là một số hợp lệ.')]:
            with self.subTest(param=param):
                response = self.client.get(reverse('product-list-create') + f'?{param}')
                self.assertEqual(response.status_code, 400)
                self.assertIn(msg, response.json()['error'])

        # Filter by price range with no result
        response = self.client.get(reverse('product-list-create') + '?min_price=10000&max_price=11000')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 0)

        # Sort by product_name ASC
        response = self.client.get(reverse('product-list-create') + '?sort_by=product_name')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self._assert_sorted(data, 'product_name')

        # Sort by list_price ASC/DESC
        for order in ['asc', 'desc']:
            response = self.client.get(reverse('product-list-create') + f'?sort_by=list_price&order_by={order}')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.content)
            prices = [Decimal(p['list_price']) for p in data]
            self.assertEqual(prices, sorted(prices, reverse=(order == 'desc')))

        # Sort by model_year DESC
        response = self.client.get(reverse('product-list-create') + '?sort_by=model_year&order_by=desc')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self._assert_sorted(data, 'model_year', reverse=True)

        # Sort by invalid field
        response = self.client.get(reverse('product-list-create') + '?sort_by=invalid_field')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Trường sắp xếp không hợp lệ.', response.json()['error'])

        # Combine filter and sort
        response = self.client.get(
            reverse('product-list-create') + '?category_id=6&min_price=1000&max_price=3000&sort_by=product_name'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self._assert_all(data, 'category_name', 'Mountain Bikes')
        self._assert_price_range(data, 1000, 3000)
        self._assert_sorted(data, 'product_name')

    # --- Product API: CRUD ---
    def test_product_list_get(self):
        response = self.client.get(reverse('product-list-create'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), Product.objects.count())
        found_product = next((item for item in data if item['product_id'] == self.product_trek_820.product_id), None)
        self.assertIsNotNone(found_product)
        self.assertEqual(found_product['product_name'], 'Trek 820 - 2016')

    def test_product_create_post_success(self):
        initial_product_count = Product.objects.count()
        new_product_data = {
            'product_id': 999999,
            'product_name': 'Brand New Custom Bike 2025',
            'brand_id': self.brand_electra.brand_id,
            'category_id': self.category_road.category_id,
            'model_year': 2025,
            'list_price': '2500.75'
        }
        response = self.client.post(
            reverse('product-list-create'),
            data=json.dumps(new_product_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Product.objects.count(), initial_product_count + 1)
        self.assertIn('message', response.json())
        self.assertEqual(response.json()['product_id'], new_product_data['product_id'])
        self.assertTrue(Product.objects.filter(product_id=new_product_data['product_id']).exists())

    def test_product_create_post_missing_field(self):
        response = self.client.post(
            reverse('product-list-create'),
            data=json.dumps({'product_id': 999998, 'product_name': 'Incomplete Product'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
        self.assertIn('Thiếu trường bắt buộc', response.json()['error'])

    def test_product_create_post_duplicate_id(self):
        response = self.client.post(
            reverse('product-list-create'),
            data=json.dumps({'product_id': self.product_trek_820.product_id,
                             'product_name': 'Duplicate Trek 820 Attempt',
                             'brand_id': self.brand_trek.brand_id,
                             'category_id': self.category_mountain.category_id,
                             'model_year': 2016,
                             'list_price': '379.99'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 409)
        self.assertIn('đã tồn tại', response.json()['error'])

    def test_product_create_post_non_existent_foreign_key(self):
        # Non-existent brand_id
        response = self.client.post(
            reverse('product-list-create'),
            data=json.dumps({'product_id': 999997,
                             'product_name': 'Product with Invalid Brand',
                             'brand_id': 99999,
                             'category_id': self.category_mountain.category_id,
                             'model_year': 2025,
                             'list_price': '100.00'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn('Brand với ID', response.json()['error'])
        # Non-existent category_id
        response = self.client.post(
            reverse('product-list-create'),
            data=json.dumps({'product_id': 999996,
                             'product_name': 'Product with Invalid Category',
                             'brand_id': self.brand_trek.brand_id,
                             'category_id': 99999,
                             'model_year': 2025,
                             'list_price': '100.00'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn('Category với ID', response.json()['error'])

    def test_product_detail_get_success(self):
        response = self.client.get(reverse('product-detail', args=[self.product_trek_820.product_id]))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['product_id'], self.product_trek_820.product_id)

    def test_product_detail_get_not_found(self):
        response = self.client.get(reverse('product-detail', args=[999999]))
        self.assertEqual(response.status_code, 404)
        self.assertIn('Sản phẩm không tồn tại', response.json()['error'])

    def test_product_update_patch_success(self):
        temp_product = Product.objects.create(
            product_id=999990,
            product_name='Temporary Product For Update',
            brand_id=self.brand_electra,
            category_id=self.category_children,
            model_year=2020,
            list_price=Decimal('100.00')
        )
        update_data = {
            'product_name': 'Temporary Product - Updated Name',
            'list_price': '105.50',
            'category_id': self.category_road.category_id
        }
        response = self.client.patch(
            reverse('product-detail', args=[temp_product.product_id]),
            data=json.dumps(update_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        temp_product.refresh_from_db()
        self.assertEqual(temp_product.product_name, 'Temporary Product - Updated Name')
        self.assertEqual(temp_product.list_price, Decimal('105.50'))
        self.assertEqual(temp_product.category_id, self.category_road)
        temp_product.delete()

    def test_product_update_patch_no_changes(self):
        original_name = self.product_trek_820.product_name
        original_price = self.product_trek_820.list_price
        response = self.client.patch(
            reverse('product-detail', args=[self.product_trek_820.product_id]),
            data=json.dumps({'product_name': original_name, 'list_price': str(original_price)}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('product_id', response.json())
        self.assertEqual(response.json()['product_name'], original_name)
        self.assertEqual(response.json()['list_price'], str(original_price))

    def test_product_update_patch_non_existent_product(self):
        response = self.client.patch(
            reverse('product-detail', args=[999999]),
            data=json.dumps({'product_name': 'Non-existent Product'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn('Sản phẩm không tồn tại', response.json()['error'])

    def test_product_update_patch_invalid_foreign_key(self):
        # Non-existent brand_id
        response = self.client.patch(
            reverse('product-detail', args=[self.product_trek_820.product_id]),
            data=json.dumps({'brand_id': 99999}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn('Brand với ID', response.json()['error'])
        # Non-existent category_id
        response = self.client.patch(
            reverse('product-detail', args=[self.product_trek_820.product_id]),
            data=json.dumps({'category_id': 99999}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn('Category với ID', response.json()['error'])

    def test_product_delete_success(self):
        temp_product_to_delete = Product.objects.create(
            product_id=999995,
            product_name='Temp Product For Delete',
            brand_id=self.brand_haro,
            category_id=self.category_children,
            model_year=2020,
            list_price=Decimal('50.00')
        )
        initial_product_count = Product.objects.count()
        response = self.client.delete(reverse('product-detail', args=[temp_product_to_delete.product_id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.json())
        self.assertEqual(Product.objects.count(), initial_product_count - 1)
        self.assertFalse(Product.objects.filter(product_id=temp_product_to_delete.product_id).exists())

    def test_product_delete_not_found(self):
        response = self.client.delete(reverse('product-detail', args=[999999]))
        self.assertEqual(response.status_code, 404)
        self.assertIn('Sản phẩm không tồn tại', response.json()['error'])

    # --- Stock API: CRUD ---
    def test_stock_list_get(self):
        response = self.client.get(reverse('stock-list-create'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), Stock.objects.count())
        found_stock = next((item for item in data if item['product_id'] == self.product_trek_820.product_id and item['store_id'] == self.store_santa_cruz.store_id), None)
        self.assertIsNotNone(found_stock)
        self.assertEqual(found_stock['quantity'], 27)

    def test_stock_create_post_success(self):
        initial_stock_count = Stock.objects.count()
        temp_product = Product.objects.create(
            product_id=999999,
            product_name='Ephemeral Test Product',
            brand_id=self.brand_electra,
            category_id=self.category_children,
            model_year=2025,
            list_price=Decimal('10.00')
        )
        temp_store = Store.objects.create(
            store_id=999999,
            store_name='Ephemeral Test Store',
            city='TestCity', state='TC', zip_code='11111'
        )
        new_stock_data = {
            'store_id': temp_store.store_id,
            'product_id': temp_product.product_id,
            'quantity': 75
        }
        response = self.client.post(
            reverse('stock-list-create'),
            data=json.dumps(new_stock_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Stock.objects.count(), initial_stock_count + 1)
        self.assertEqual(response.json()['quantity'], 75)
        self.assertTrue(Stock.objects.filter(
            store_id=temp_store,
            product_id=temp_product,
            quantity=75
        ).exists())
        Stock.objects.get(store_id=temp_store, product_id=temp_product).delete()
        temp_product.delete()
        temp_store.delete()

    def test_stock_create_post_missing_field(self):
        response = self.client.post(
            reverse('stock-list-create'),
            data=json.dumps({'store_id': self.store_santa_cruz.store_id, 'product_id': self.product_trek_820.product_id}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
        self.assertIn('Thiếu trường bắt buộc', response.json()['error'])

    def test_stock_create_post_duplicate_entry(self):
        response = self.client.post(
            reverse('stock-list-create'),
            data=json.dumps({'store_id': self.store_santa_cruz.store_id,
                             'product_id': self.product_trek_820.product_id,
                             'quantity': 10}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 409)
        self.assertIn('đã tồn tại', response.json()['error'])

    def test_stock_create_post_non_existent_foreign_key(self):
        # Non-existent store_id
        response = self.client.post(
            reverse('stock-list-create'),
            data=json.dumps({'store_id': 999999,
                             'product_id': self.product_trek_820.product_id,
                             'quantity': 10}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn('Cửa hàng với ID', response.json()['error'])
        # Non-existent product_id
        response = self.client.post(
            reverse('stock-list-create'),
            data=json.dumps({'store_id': self.store_santa_cruz.store_id,
                             'product_id': 999999,
                             'quantity': 10}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn('Sản phẩm với ID', response.json()['error'])

    def test_stock_detail_get_success(self):
        response = self.client.get(reverse('stock-detail', args=[self.stock_trek_820_santa_cruz.store_id.store_id, self.stock_trek_820_santa_cruz.product_id.product_id]))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['store_id'], self.store_santa_cruz.store_id)
        self.assertEqual(data['product_id'], self.product_trek_820.product_id)
        self.assertEqual(data['quantity'], 27)

    def test_stock_detail_get_not_found(self):
        # Non-existent product at existing store
        response = self.client.get(reverse('stock-detail', args=[self.store_santa_cruz.store_id, 999999]))
        self.assertEqual(response.status_code, 404)
        self.assertIn('Bản ghi tồn kho không tồn tại', response.json()['error'])
        # Non-existent store for existing product
        response = self.client.get(reverse('stock-detail', args=[999999, self.product_trek_820.product_id]))
        self.assertEqual(response.status_code, 404)
        self.assertIn('Bản ghi tồn kho không tồn tại', response.json()['error'])

    def test_stock_update_patch_success(self):
        temp_stock_product = Product.objects.create(
            product_id=999980, product_name='Update Test Product', brand_id=self.brand_electra, category_id=self.category_children, model_year=2020, list_price=Decimal('100.00')
        )
        temp_stock_store = Store.objects.create(
            store_id=999980, store_name='Update Test Store', city='UCity', state='UT', zip_code='00000'
        )
        temp_stock = Stock.objects.create(store_id=temp_stock_store, product_id=temp_stock_product, quantity=50)
        new_quantity = 15
        update_data = {'quantity': new_quantity}
        response = self.client.patch(
            reverse('stock-detail', args=[temp_stock.store_id.store_id, temp_stock.product_id.product_id]),
            data=json.dumps(update_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        temp_stock.refresh_from_db()
        self.assertEqual(temp_stock.quantity, new_quantity)
        temp_stock.delete()
        temp_stock_product.delete()
        temp_stock_store.delete()

    def test_stock_update_patch_no_changes(self):
        current_quantity = self.stock_trek_820_santa_cruz.quantity
        response = self.client.patch(
            reverse('stock-detail', args=[self.stock_trek_820_santa_cruz.store_id.store_id, self.stock_trek_820_santa_cruz.product_id.product_id]),
            data=json.dumps({'quantity': current_quantity}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('Không có thay đổi nào được thực hiện', response.json()['message'])

    def test_stock_update_patch_non_existent_stock(self):
        response = self.client.patch(
            reverse('stock-detail', args=[999999, 999999]),
            data=json.dumps({'quantity': 5}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn('Bản ghi tồn kho không tồn tại', response.json()['error'])

    def test_stock_update_patch_missing_quantity_field(self):
        response = self.client.patch(
            reverse('stock-detail', args=[self.stock_trek_820_santa_cruz.store_id.store_id, self.stock_trek_820_santa_cruz.product_id.product_id]),
            data=json.dumps({'some_other_field': 'value'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('Thiếu trường bắt buộc: quantity', response.json()['error'])

    def test_stock_delete_success(self):
        temp_delete_product = Product.objects.create(
            product_id=999970, product_name='Delete Test Product', brand_id=self.brand_haro, category_id=self.category_road, model_year=2021, list_price=Decimal('500.00')
        )
        temp_delete_store = Store.objects.create(
            store_id=999970, store_name='Delete Test Store', city='DCity', state='DT', zip_code='22222'
        )
        temp_stock_to_delete = Stock.objects.create(store_id=temp_delete_store, product_id=temp_delete_product, quantity=30)
        initial_stock_count = Stock.objects.count()
        response = self.client.delete(
            reverse('stock-detail', args=[temp_stock_to_delete.store_id.store_id, temp_stock_to_delete.product_id.product_id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.json())
        self.assertEqual(Stock.objects.count(), initial_stock_count - 1)
        self.assertFalse(Stock.objects.filter(
            store_id=temp_stock_to_delete.store_id,
            product_id=temp_stock_to_delete.product_id
        ).exists())
        temp_delete_product.delete()
        temp_delete_store.delete()

    def test_stock_delete_not_found(self):
        response = self.client.delete(reverse('stock-detail', args=[999999, 999999]))
        self.assertEqual(response.status_code, 404)
        self.assertIn('Bản ghi tồn kho không tồn tại', response.json()['error'])