from django.test import TestCase, Client
from django.urls import reverse
import json
from decimal import Decimal 

# Import models
from .models import Category, Brand, Product, Stock
from sales.models import Store 

class ProductionAPITests(TestCase):
    """
    Tests for Product and Stock APIs in the production app.
    Data is loaded from a Django fixture generated from load_data_modified.sql.
    """
    # Load data from the fixture file
    fixtures = ['production_initial_data'] 

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()

        # Retrieve common test objects from the loaded fixture data
        # These objects will be used across multiple test methods
        cls.brand_electra = Brand.objects.get(brand_id=1)
        cls.brand_haro = Brand.objects.get(brand_id=2)
        cls.brand_trek = Brand.objects.get(brand_id=9)
        cls.brand_ritchey = Brand.objects.get(brand_id=5)
        cls.brand_surly = Brand.objects.get(brand_id=8)
        cls.brand_sun_bicycles = Brand.objects.get(brand_id=7)

        cls.category_children = Category.objects.get(category_id=1)
        cls.category_comfort = Category.objects.get(category_id=2)
        cls.category_cruisers = Category.objects.get(category_id=3)
        cls.category_cyclocross = Category.objects.get(category_id=4)
        cls.category_electric = Category.objects.get(category_id=5)
        cls.category_mountain = Category.objects.get(category_id=6)
        cls.category_road = Category.objects.get(category_id=7)
        
        cls.store_santa_cruz = Store.objects.get(store_id=1)
        cls.store_baldwin = Store.objects.get(store_id=2)
        cls.store_rowlett = Store.objects.get(store_id=3)

        cls.product_trek_820 = Product.objects.get(product_id=1)
        cls.product_ritchey = Product.objects.get(product_id=2)
        cls.product_surly_wednesday = Product.objects.get(product_id=3)
        cls.product_electra_townie_21d = Product.objects.get(product_id=12)
        cls.product_electra_townie_7d_boys = Product.objects.get(product_id=101)
        cls.product_electra_superbolt = Product.objects.get(product_id=289)
        cls.product_electra_tiger_shark = Product.objects.get(product_id=293)
        cls.product_sun_electrolite = Product.objects.get(product_id=60)
        
        # Get a specific stock object that we know exists from the fixture for detailed tests
        cls.stock_trek_820_santa_cruz = Stock.objects.get(store_id=cls.store_santa_cruz, product_id=cls.product_trek_820)
        cls.stock_ritchey_santa_cruz = Stock.objects.get(store_id=cls.store_santa_cruz, product_id=cls.product_ritchey)
        cls.stock_electra_superbolt_santa_cruz = Stock.objects.get(store_id=cls.store_santa_cruz, product_id=cls.product_electra_superbolt)
        

    # --- Tests for Product API ---

    def test_product_list_get(self):
        """
        Test GET /api/production/products/ endpoint.
        Should return a list of all products.
        """
        response = self.client.get(reverse('product-list-create'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), Product.objects.count()) # Verify count matches total products in fixture
        
        # Verify a specific product's data (using product_id=1 from SQL)
        found_product = next((item for item in data if item['product_id'] == self.product_trek_820.product_id), None)
        self.assertIsNotNone(found_product)
        self.assertEqual(found_product['product_name'], 'Trek 820 - 2016')
        self.assertEqual(found_product['brand_name'], 'Trek')
        self.assertEqual(found_product['category_name'], 'Mountain Bikes')
        self.assertEqual(found_product['model_year'], 2016)
        self.assertEqual(found_product['list_price'], '379.99') 

    def test_product_create_post_success(self):
        """
        Test POST /api/production/products/ for successful creation.
        Uses a product_id that is highly unlikely to exist in the provided SQL data.
        """
        initial_product_count = Product.objects.count()
        new_product_data = {
            'product_id': 999999, # A very large ID to ensure it's new
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
        self.assertEqual(response.status_code, 201) # 201 Created
        self.assertEqual(Product.objects.count(), initial_product_count + 1)
        self.assertIn('message', response.json())
        self.assertEqual(response.json()['product_id'], new_product_data['product_id'])
        self.assertTrue(Product.objects.filter(product_id=new_product_data['product_id']).exists())

    def test_product_create_post_missing_field(self):
        """
        Test POST /api/production/products/ with missing required fields.
        """
        response = self.client.post(
            reverse('product-list-create'),
            data=json.dumps({'product_id': 999998, 'product_name': 'Incomplete Product'}), # Missing brand_id, category_id etc.
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
        self.assertIn('Thiếu trường bắt buộc', response.json()['error'])

    def test_product_create_post_duplicate_id(self):
        """
        Test POST /api/production/products/ with an already existing product_id.
        Should return a 409 Conflict.
        """
        response = self.client.post(
            reverse('product-list-create'),
            data=json.dumps({'product_id': self.product_trek_820.product_id, # Existing ID from fixture
                             'product_name': 'Duplicate Trek 820 Attempt',
                             'brand_id': self.brand_trek.brand_id,
                             'category_id': self.category_mountain.category_id,
                             'model_year': 2016,
                             'list_price': '379.99'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 409) # 409 Conflict
        self.assertIn('đã tồn tại', response.json()['error'])

    def test_product_create_post_non_existent_foreign_key(self):
        """
        Test POST /api/production/products/ with non-existent brand_id or category_id.
        Should return a 404 Not Found.
        """
        # Test non-existent brand_id
        response = self.client.post(
            reverse('product-list-create'),
            data=json.dumps({'product_id': 999997,
                             'product_name': 'Product with Invalid Brand',
                             'brand_id': 99999, # Highly unlikely to exist
                             'category_id': self.category_mountain.category_id,
                             'model_year': 2025,
                             'list_price': '100.00'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404) 
        self.assertIn('Brand với ID', response.json()['error'])

        # Test non-existent category_id
        response = self.client.post(
            reverse('product-list-create'),
            data=json.dumps({'product_id': 999996,
                             'product_name': 'Product with Invalid Category',
                             'brand_id': self.brand_trek.brand_id,
                             'category_id': 99999, # Highly unlikely to exist
                             'model_year': 2025,
                             'list_price': '100.00'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn('Category với ID', response.json()['error'])


    def test_product_detail_get_success(self):
        """
        Test GET /api/production/products/<product_id>/ for existing product.
        """
        response = self.client.get(reverse('product-detail', args=[self.product_trek_820.product_id]))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['product_id'], self.product_trek_820.product_id)
        self.assertEqual(data['product_name'], 'Trek 820 - 2016')
        self.assertEqual(data['brand_name'], 'Trek')
        self.assertEqual(data['category_name'], 'Mountain Bikes')
        self.assertEqual(data['model_year'], 2016)
        self.assertEqual(data['list_price'], '379.99')

    def test_product_detail_get_not_found(self):
        """
        Test GET /api/production/products/<product_id>/ for non-existent product.
        Should return 404 Not Found.
        """
        response = self.client.get(reverse('product-detail', args=[999999])) # Non-existent ID
        self.assertEqual(response.status_code, 404)
        self.assertIn('Sản phẩm không tồn tại', response.json()['error'])

    def test_product_update_patch_success(self):
        """
        Test PATCH /api/production/products/<product_id>/ for successful update.
        """
        # Update product_surly_wednesday (product_id=3)
        update_data = {
            'product_name': 'Surly Wednesday Frameset - Updated',
            'list_price': '1050.00',
            'category_id': self.category_cyclocross.category_id # Change category
        }
        response = self.client.patch(
            reverse('product-detail', args=[self.product_surly_wednesday.product_id]),
            data=json.dumps(update_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.product_surly_wednesday.refresh_from_db() # Reload the object from DB to get updated values
        self.assertEqual(self.product_surly_wednesday.product_name, 'Surly Wednesday Frameset - Updated')
        self.assertEqual(self.product_surly_wednesday.list_price, Decimal('1050.00'))
        self.assertEqual(self.product_surly_wednesday.category_id, self.category_cyclocross)
        self.assertEqual(response.json()['product_name'], 'Surly Wednesday Frameset - Updated')

    def test_product_update_patch_no_changes(self):
        """
        Test PATCH /api/production/products/<product_id>/ when no actual changes are made.
        Should return 200 OK with current data.
        """
        original_name = self.product_trek_820.product_name
        response = self.client.patch(
            reverse('product-detail', args=[self.product_trek_820.product_id]),
            data=json.dumps({'product_name': original_name}), # Same data
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('product_id', response.json()) # Should return current data
        # Check if actual message is returned
        # self.assertIn('Không có thay đổi nào được thực hiện', response.json()['message']) 
        # The view currently returns the updated object, not a "no changes" message for Product.
        # This test ensures it still returns 200 OK.

    def test_product_update_patch_non_existent_product(self):
        """
        Test PATCH /api/production/products/<product_id>/ for non-existent product.
        Should return 404 Not Found.
        """
        response = self.client.patch(
            reverse('product-detail', args=[999999]),
            data=json.dumps({'product_name': 'Non-existent Product'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn('Sản phẩm không tồn tại', response.json()['error'])

    def test_product_update_patch_invalid_foreign_key(self):
        """
        Test PATCH /api/production/products/<product_id>/ with non-existent foreign key ID.
        Should return 404 Not Found for the related object.
        """
        # Test update with non-existent brand_id
        response = self.client.patch(
            reverse('product-detail', args=[self.product_trek_820.product_id]),
            data=json.dumps({'brand_id': 99999}), # Non-existent brand ID
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn('Brand với ID', response.json()['error'])

        # Test update with non-existent category_id
        response = self.client.patch(
            reverse('product-detail', args=[self.product_trek_820.product_id]),
            data=json.dumps({'category_id': 99999}), # Non-existent category ID
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn('Category với ID', response.json()['error'])


    def test_product_delete_success(self):
        """
        Test DELETE /api/production/products/<product_id>/ for successful deletion.
        """
        initial_product_count = Product.objects.count()
        # Delete product_electra_townie_21d (product_id=12)
        response = self.client.delete(reverse('product-detail', args=[self.product_electra_townie_21d.product_id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.json())
        self.assertEqual(Product.objects.count(), initial_product_count - 1)
        self.assertFalse(Product.objects.filter(product_id=self.product_electra_townie_21d.product_id).exists())

    def test_product_delete_not_found(self):
        """
        Test DELETE /api/production/products/<product_id>/ for non-existent product.
        Should return 404 Not Found.
        """
        response = self.client.delete(reverse('product-detail', args=[999999])) # Non-existent ID
        self.assertEqual(response.status_code, 404)
        self.assertIn('Sản phẩm không tồn tại', response.json()['error'])

    # --- Tests for Stock API ---

    def test_stock_list_get(self):
        """
        Test GET /api/production/stocks/ endpoint.
        Should return a list of all stock entries.
        """
        response = self.client.get(reverse('stock-list-create'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), Stock.objects.count()) # Verify count matches total stocks in fixture

        # Verify a specific stock entry's data (product_id=1, store_id=1)
        found_stock = next((item for item in data if item['product_id'] == self.product_trek_820.product_id and item['store_id'] == self.store_santa_cruz.store_id), None)
        self.assertIsNotNone(found_stock)
        self.assertEqual(found_stock['quantity'], 27) 
        self.assertEqual(found_stock['store_name'], 'Santa Cruz Bikes')
        self.assertEqual(found_stock['product_name'], 'Trek 820 - 2016')

    def test_stock_create_post_success(self):
        """
        Test POST /api/production/stocks/ for successful creation.
        Uses a unique (store_id, product_id) combination guaranteed to be new.
        """
        initial_stock_count = Stock.objects.count()
        
        # Create a temporary unique product and store for this test to ensure no conflicts
        # Using very high IDs to avoid conflicts with loaded fixture data
        temp_brand = Brand.objects.create(brand_id=999990, brand_name='TempBrand')
        temp_category = Category.objects.create(category_id=999990, category_name='TempCategory')
        temp_product = Product.objects.create(
            product_id=999999, # Highly unlikely to exist
            product_name='Temporary Test Product', 
            brand_id=temp_brand, 
            category_id=temp_category, 
            model_year=2025, 
            list_price=Decimal('1.00')
        )
        temp_store = Store.objects.create(
            store_id=999999, # Highly unlikely to exist
            store_name='Temporary Test Store', 
            city='TempCity', state='TS', zip_code='12345'
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
        self.assertEqual(response.status_code, 201) # 201 Created
        self.assertEqual(Stock.objects.count(), initial_stock_count + 1)
        self.assertEqual(response.json()['quantity'], 75)
        self.assertTrue(Stock.objects.filter(
            store_id=temp_store,
            product_id=temp_product,
            quantity=75
        ).exists())

        # Clean up temporary objects (optional but good practice for per-test-method setup)
        temp_stock_created = Stock.objects.get(store_id=temp_store, product_id=temp_product)
        temp_stock_created.delete()
        temp_product.delete()
        temp_brand.delete()
        temp_category.delete()
        temp_store.delete()
        
    def test_stock_create_post_missing_field(self):
        """
        Test POST /api/production/stocks/ with missing required fields (e.g., quantity).
        """
        response = self.client.post(
            reverse('stock-list-create'),
            data=json.dumps({'store_id': self.store_santa_cruz.store_id, 'product_id': self.product_trek_820.product_id}), # Missing quantity
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
        self.assertIn('Thiếu trường bắt buộc', response.json()['error'])

    def test_stock_create_post_duplicate_entry(self):
        """
        Test POST /api/production/stocks/ with an already existing (store_id, product_id) pair.
        Should return a 409 Conflict due to unique_together constraint.
        """
        # Using (store_id=1, product_id=1) which is (Santa Cruz, Trek 820)
        response = self.client.post(
            reverse('stock-list-create'),
            data=json.dumps({'store_id': self.store_santa_cruz.store_id,
                             'product_id': self.product_trek_820.product_id,
                             'quantity': 10}), # Attempt to create duplicate of existing stock
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 409) # 409 Conflict
        self.assertIn('đã tồn tại', response.json()['error'])
        self.assertIn('Bản ghi tồn kho cho sản phẩm này tại cửa hàng này đã tồn tại', response.json()['error'])

    def test_stock_create_post_non_existent_foreign_key(self):
        """
        Test POST /api/production/stocks/ with non-existent store_id or product_id.
        Should return 404 Not Found.
        """
        # Test with non-existent store_id
        response = self.client.post(
            reverse('stock-list-create'),
            data=json.dumps({'store_id': 999999, # Non-existent store ID
                             'product_id': self.product_trek_820.product_id,
                             'quantity': 10}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn('Cửa hàng với ID', response.json()['error'])

        # Test with non-existent product_id
        response = self.client.post(
            reverse('stock-list-create'),
            data=json.dumps({'store_id': self.store_santa_cruz.store_id,
                             'product_id': 999999, # Non-existent product ID
                             'quantity': 10}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn('Sản phẩm với ID', response.json()['error'])

    def test_stock_detail_get_success(self):
        """
        Test GET /api/production/stocks/<store_id>/<product_id>/ for existing stock.
        """
        response = self.client.get(reverse('stock-detail', args=[self.stock_trek_820_santa_cruz.store_id.store_id, self.stock_trek_820_santa_cruz.product_id.product_id]))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['store_id'], self.store_santa_cruz.store_id)
        self.assertEqual(data['product_id'], self.product_trek_820.product_id)
        self.assertEqual(data['quantity'], 27) 
        self.assertEqual(data['store_name'], 'Santa Cruz Bikes')
        self.assertEqual(data['product_name'], 'Trek 820 - 2016')

    def test_stock_detail_get_not_found(self):
        """
        Test GET /api/production/stocks/<store_id>/<product_id>/ for non-existent stock.
        Should return 404 Not Found.
        """
        # Non-existent product at existing store
        response = self.client.get(reverse('stock-detail', args=[self.store_santa_cruz.store_id, 999999]))
        self.assertEqual(response.status_code, 404)
        self.assertIn('Bản ghi tồn kho không tồn tại', response.json()['error'])

        # Non-existent store for existing product
        response = self.client.get(reverse('stock-detail', args=[999999, self.product_trek_820.product_id]))
        self.assertEqual(response.status_code, 404)
        self.assertIn('Bản ghi tồn kho không tồn tại', response.json()['error'])

    def test_stock_update_patch_success(self):
        """
        Test PATCH /api/production/stocks/<store_id>/<product_id>/ for successful update.
        """
        # Update product_ritchey at store_santa_cruz (stock_id=1, product_id=2, quantity=5)
        stock_to_update = self.stock_ritchey_santa_cruz
        new_quantity = 15

        update_data = {
            'quantity': new_quantity
        }
        response = self.client.patch(
            reverse('stock-detail', args=[stock_to_update.store_id.store_id, stock_to_update.product_id.product_id]),
            data=json.dumps(update_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        stock_to_update.refresh_from_db() # Reload the object from DB
        self.assertEqual(stock_to_update.quantity, new_quantity)
        self.assertEqual(response.json()['quantity'], new_quantity)

    def test_stock_update_patch_no_changes(self):
        """
        Test PATCH /api/production/stocks/<store_id>/<product_id>/ when no actual changes are made.
        Should return 200 OK with a specific message.
        """
        current_quantity = self.stock_trek_820_santa_cruz.quantity
        response = self.client.patch(
            reverse('stock-detail', args=[self.stock_trek_820_santa_cruz.store_id.store_id, self.stock_trek_820_santa_cruz.product_id.product_id]),
            data=json.dumps({'quantity': current_quantity}), # Same quantity
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('Không có thay đổi nào được thực hiện', response.json()['message']) 

    def test_stock_update_patch_non_existent_stock(self):
        """
        Test PATCH /api/production/stocks/<store_id>/<product_id>/ for non-existent stock.
        Should return 404 Not Found.
        """
        response = self.client.patch(
            reverse('stock-detail', args=[999999, 999999]), # Non-existent combination
            data=json.dumps({'quantity': 5}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn('Bản ghi tồn kho không tồn tại', response.json()['error'])

    def test_stock_update_patch_missing_quantity_field(self):
        """
        Test PATCH /api/production/stocks/<store_id>/<product_id>/ with missing quantity field.
        """
        response = self.client.patch(
            reverse('stock-detail', args=[self.stock_trek_820_santa_cruz.store_id.store_id, self.stock_trek_820_santa_cruz.product_id.product_id]),
            data=json.dumps({'some_other_field': 'value'}), # Missing quantity
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400) # Bad Request
        self.assertIn('Thiếu trường bắt buộc: quantity', response.json()['error'])

    def test_stock_delete_success(self):
        """
        Test DELETE /api/production/stocks/<store_id>/<product_id>/ for successful deletion.
        """
        initial_stock_count = Stock.objects.count()
        # Delete stock for Electra Superbolt at Santa Cruz (store_id=1, product_id=289)
        stock_to_delete = self.stock_electra_superbolt_santa_cruz
        
        response = self.client.delete(
            reverse('stock-detail', args=[stock_to_delete.store_id.store_id, stock_to_delete.product_id.product_id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.json())
        self.assertEqual(Stock.objects.count(), initial_stock_count - 1)
        self.assertFalse(Stock.objects.filter(
            store_id=stock_to_delete.store_id, 
            product_id=stock_to_delete.product_id
        ).exists())

    def test_stock_delete_not_found(self):
        """
        Test DELETE /api/production/stocks/<store_id>/<product_id>/ for non-existent stock.
        Should return 404 Not Found.
        """
        response = self.client.delete(reverse('stock-detail', args=[999999, 999999])) # Non-existent combination
        self.assertEqual(response.status_code, 404)
        self.assertIn('Bản ghi tồn kho không tồn tại', response.json()['error'])