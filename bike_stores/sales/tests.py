from django.test import TestCase, Client
from django.urls import reverse
from .models import Customer, Store, Staff, Order, OrderItem
from production.models import Product, Brand, Category
import json
from datetime import date

class SalesAPITestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self._create_sample_data()

    def _create_sample_data(self):
        # Store, Customer, Staff
        self.store = Store.objects.create(
            store_id=1, store_name="Test Store", phone="123", email="store@test.com",
            street="123 St", city="City", state="ST", zip_code="12345"
        )
        self.customer = Customer.objects.create(
            customer_id=1, first_name="John", last_name="Doe", email="john@example.com"
        )
        self.staff = Staff.objects.create(
            staff_id=1, first_name="Jane", last_name="Smith", email="jane@example.com",
            active=True, store_id=self.store
        )
        # Brand, Category, Product
        self.brand = Brand.objects.create(brand_id=1, brand_name="TestBrand")
        self.category = Category.objects.create(category_id=1, category_name="TestCategory")
        self.product = Product.objects.create(
            product_id=1, product_name="Bike", brand_id=self.brand, category_id=self.category,
            model_year=2024, list_price=1000
        )
        # Order, OrderItem
        self.order = Order.objects.create(
            order_id=1, customer_id=self.customer, order_status=1,
            order_date=date.today(), required_date=date.today(),
            store_id=self.store, staff_id=self.staff
        )
        self.order_item = OrderItem.objects.create(
            order_id=self.order, item_id=1, product_id=self.product,
            quantity=2, list_price=1000, discount=0
        )

    # ----------- CUSTOMER TESTS -----------
    def test_customer_list(self):
        url = reverse('customer-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_create_customer(self):
        url = reverse('customer-list')
        data = {
            "customer_id": 2,
            "first_name": "Alice",
            "last_name": "Wonder",
            "email": "alice@example.com"
        }
        response = self.client.post(url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['first_name'], "Alice")

    def test_get_customer_detail(self):
        url = reverse('customer-detail', args=[self.customer.customer_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['first_name'], "John")

    def test_update_customer(self):
        url = reverse('customer-detail', args=[self.customer.customer_id])
        data = {"first_name": "Johnny"}
        response = self.client.patch(url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['first_name'], "Johnny")

    def test_delete_customer(self):
        url = reverse('customer-detail', args=[self.customer.customer_id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('được xóa thành công', response.json()['message'])

    # ----------- ORDER TESTS -----------
    def test_order_list(self):
        url = reverse('order-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_create_order(self):
        url = reverse('order-list')
        data = {
            "order_id": 2,
            "customer_id": self.customer.customer_id,
            "order_status": 1,
            "order_date": str(date.today()),
            "required_date": str(date.today()),
            "store_id": self.store.store_id,
            "staff_id": self.staff.staff_id
        }
        response = self.client.post(url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['order_id'], 2)

    # ----------- ORDER ITEM TESTS -----------
    def test_orderitem_list(self):
        url = reverse('orderitem-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_create_orderitem(self):
        url = reverse('orderitem-list')
        data = {
            "order_id": self.order.order_id,
            "item_id": 2,
            "product_id": self.product.product_id,
            "quantity": 1,
            "list_price": 500,
            "discount": 0
        }
        response = self.client.post(url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['item_id'], 2)

    # ----------- STORE TESTS -----------
    def test_store_list(self):
        url = reverse('store-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_create_store(self):
        url = reverse('store-list')
        data = {
            "store_id": 2,
            "store_name": "New Store",
            "phone": "456",
            "email": "newstore@test.com",
            "street": "456 St",
            "city": "New City",
            "state": "NC",
            "zip_code": "67890"
        }
        response = self.client.post(url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['store_name'], "New Store")

    def test_get_store_detail(self):
        url = reverse('store-detail', args=[self.store.store_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['store_name'], "Test Store")

    def test_update_store(self):
        url = reverse('store-detail', args=[self.store.store_id])
        data = {"store_name": "Updated Store"}
        response = self.client.patch(url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['store_name'], "Updated Store")

    def test_delete_store(self):
        # Tạo store mới không liên kết với staff/order nào
        store = Store.objects.create(
            store_id=999,
            store_name="Delete Store",
            phone="000",
            email="delete@store.com",
            street="None",
            city="None",
            state="NA",
            zip_code="00000"
        )
        url = reverse('store-detail', args=[store.store_id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('được xóa thành công', response.json()['message'])

    # ----------- STAFF TESTS -----------
    def test_staff_list(self):
        url = reverse('staff-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_create_staff(self):
        url = reverse('staff-list')
        data = {
            "staff_id": 2,
            "first_name": "Bob",
            "last_name": "Marley",
            "email": "bob@example.com",
            "active": True,
            "store_id": self.store.store_id
        }
        response = self.client.post(url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['first_name'], "Bob")

    def test_get_staff_detail(self):
        url = reverse('staff-detail', args=[self.staff.staff_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['first_name'], "Jane")

    def test_update_staff(self):
        url = reverse('staff-detail', args=[self.staff.staff_id])
        data = {"first_name": "Janet"}
        response = self.client.patch(url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['first_name'], "Janet")

    def test_delete_staff(self):
        staff = Staff.objects.create(
            staff_id=999,
            first_name="Delete",
            last_name="Staff",
            email="delete@staff.com",
            active=True,
            store_id=self.store
        )
        url = reverse('staff-detail', args=[staff.staff_id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('được xóa thành công', response.json()['message'])