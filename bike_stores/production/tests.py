from django.test import TestCase, Client
from django.urls import reverse
from decimal import Decimal
from production.models import Category, Brand, Product, Stock
from sales.models import Store
from django.contrib.auth.models import User
from django.urls import reverse

import json

class ProductionAPITests(TestCase):

    # Tải dữ liệu
    fixtures = ['production_initial_data']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()

        cls.brand_electra = Brand.objects.get(brand_id=1)
        cls.brand_haro = Brand.objects.get(brand_id=2)
        cls.brand_heller = Brand.objects.get(brand_id=3)
        cls.brand_purecycles = Brand.objects.get(brand_id=4)
        cls.brand_ritchey = Brand.objects.get(brand_id=5)
        cls.brand_strider = Brand.objects.get(brand_id=6)
        cls.brand_sun_bicycles = Brand.objects.get(brand_id=7)
        cls.brand_surly = Brand.objects.get(brand_id=8)
        cls.brand_trek = Brand.objects.get(brand_id=9)

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

        # Lấy các đối tượng sản phẩm cụ thể từ fixture
        # Lấy product_id
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
        cls.product_electra_townie_21d = Product.objects.get(product_id=12)
        cls.product_electra_cruiser_24 = Product.objects.get(product_id=13)
        cls.product_electra_hawaii_16 = Product.objects.get(product_id=14)
        cls.product_purecycles_vine = Product.objects.get(product_id=17)
        cls.product_purecycles_western = Product.objects.get(product_id=18)
        cls.product_electra_hawaii_20 = Product.objects.get(product_id=23)
        cls.product_electra_comfort_21d = Product.objects.get(product_id=24)
        cls.product_electra_comfort_7d = Product.objects.get(product_id=25)

        cls.stock_trek_820_santa_cruz = Stock.objects.get(store_id=cls.store_santa_cruz, product_id=cls.product_trek_820)
        cls.stock_ritchey_santa_cruz = Stock.objects.get(store_id=cls.store_santa_cruz, product_id=cls.product_ritchey)

    #--- Trích xuất ID sản phẩm cho việc Verify sắp xếp ---
    def _get_product_ids(self, data):
        return [item['product_id'] for item in data]

    # --- Test case lọc sản phẩm theo Brand ---
    def test_filter_by_brand(self):
        """
        Kiểm tra lọc sản phẩm theo brand_id.
        """
        # Lọc sản phẩm của Trek (brand_id=9)
        response = self.client.get(reverse('product-list-create') + '?brand_id=9')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)

        expected_trek_product_ids = sorted([1, 4, 7, 8, 9, 29, 32, 34, 39, 40, 42, 43, 47, 48, 49, 50, 51, 54, 55, 56, 57, 58, 59, 61, 62, 63, 83, 86, 87, 88, 89, 90, 91, 112, 113, 114, 115, 116, 117, 118, 119, 120, 123, 125, 129, 130, 132, 133, 134, 135, 136, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 162, 165, 166, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 193, 194, 196, 197, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 262, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 316, 317, 318, 319, 320, 321])
        self.assertEqual(len(data), len(expected_trek_product_ids))
        self.assertEqual(self._get_product_ids(data), expected_trek_product_ids)
        for product in data:
            self.assertEqual(product['brand_name'], 'Trek')

        # Lọc sản phẩm của Electra (brand_id=1)
        response = self.client.get(reverse('product-list-create') + '?brand_id=1')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)

        expected_electra_product_ids = sorted([12, 13, 14, 15, 16, 20, 21, 22, 23, 24, 25, 26, 64, 70, 74, 75, 76, 77, 81, 82, 95, 96, 97, 98, 99, 100, 101, 102, 191, 192, 195, 198, 199, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315]) # Đã đếm thủ công từ load_data_modified.sql
        self.assertEqual(len(data), len(expected_electra_product_ids)) # Sửa thành 135 == 135
        self.assertEqual(self._get_product_ids(data), expected_electra_product_ids)
        for product in data:
            self.assertEqual(product['brand_name'], 'Electra')

        # Lọc bằng brand_id không tồn tại
        response = self.client.get(reverse('product-list-create') + '?brand_id=99999')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 0)

        # Lọc với brand_id không hợp lệ
        response = self.client.get(reverse('product-list-create') + '?brand_id=abc')
        self.assertEqual(response.status_code, 400)
        self.assertIn('brand_id phải là một số nguyên hợp lệ.', response.json()['error'])


    #--- Test case lọc sản phẩm theo Category ---
    def test_filter_by_category(self):
        """
        Kiểm tra lọc sản phẩm theo category_id.
        """
        # Lọc sản phẩm của Mountain Bikes (category_id=6)
        response = self.client.get(reverse('product-list-create') + '?category_id=6')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)

        expected_mountain_product_ids = sorted([1, 2, 3, 4, 5, 6, 7, 8, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142])
        self.assertEqual(len(data), len(expected_mountain_product_ids))
        self.assertEqual(self._get_product_ids(data), expected_mountain_product_ids)
        for product in data:
            self.assertEqual(product['category_name'], 'Mountain Bikes')

        # Lọc sản phẩm của Road Bikes (category_id=7)
        response = self.client.get(reverse('product-list-create') + '?category_id=7')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)

        expected_road_product_ids = sorted([48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 316, 317, 318, 319, 320, 321]) # Đã đếm thủ công từ load_data_modified.sql
        self.assertEqual(len(data), len(expected_road_product_ids))
        self.assertEqual(self._get_product_ids(data), expected_road_product_ids)
        for product in data:
            self.assertEqual(product['category_name'], 'Road Bikes')

        # Lọc bằng category_id không tồn tại
        response = self.client.get(reverse('product-list-create') + '?category_id=99999')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 0)

        # Lọc với category_id không hợp lệ
        response = self.client.get(reverse('product-list-create') + '?category_id=xyz')
        self.assertEqual(response.status_code, 400)
        self.assertIn('category_id phải là một số nguyên hợp lệ.', response.json()['error'])
    
    #--- Test case lọc sản phẩm theo khoảng giá ---
    def test_filter_by_price_range(self):
        """
        Kiểm tra lọc sản phẩm theo khoảng giá.
        """
        # Giá từ 500.00 đến 1000.00
        response = self.client.get(reverse('product-list-create') + '?min_price=500&max_price=1000')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)

        # ID sản phẩm trong khoảng 500-1000
        expected_product_ids_500_1000 = sorted([
            2, 3, 12, 15, 16, 20, 24, 26, 27, 29, 30, 35, 36, 38, 44, 45, 52, 53, 70, 72, 73, 
            75, 77, 78, 80, 82, 103, 105, 114, 116, 118, 123, 129, 130, 158, 166, 167, 
            178, 179, 180, 212, 214, 215, 216, 217, 219, 223, 225, 226, 231, 233, 234, 
            235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 
            254, 255, 256, 257, 260, 261, 299, 300, 301, 304, 305, 306, 307, 308, 309, 
            310, 311, 312, 314, 315])
        # Kiểm tra lại số lượng thực tế từ file SQL:
        self.assertEqual(len(data), len(expected_product_ids_500_1000))
        self.assertEqual(self._get_product_ids(data), expected_product_ids_500_1000)

        for product in data:
            price = Decimal(product['list_price'])
            self.assertTrue(Decimal('500.00') <= price <= Decimal('1000.00'))

        # Giá trên 3000
        response = self.client.get(reverse('product-list-create') + '?min_price=3000')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        # ID sản phẩm trên 3000
        expected_product_ids_over_3000 = sorted([
            7, 40, 43, 47, 49, 50, 51, 54, 56, 58, 61, 62, 63, 115, 140, 142, 
            146, 148, 149, 150, 153, 154, 155, 156, 157, 160, 169, 171, 172, 
            173, 174, 175, 176, 177, 184, 186, 188, 194, 200, 201, 202, 203, 
            204, 205, 206, 207, 320, 321
        ])
        self.assertEqual(len(data), len(expected_product_ids_over_3000))
        self.assertEqual(self._get_product_ids(data), expected_product_ids_over_3000)

        for product in data:
            price = Decimal(product['list_price'])
            self.assertTrue(price >= Decimal('3000.00'))

        # Giá dưới 300
        response = self.client.get(reverse('product-list-create') + '?max_price=300')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        # ID sản phẩm dưới 300
        expected_product_ids_under_300 = sorted([
            13, 14, 21, 22, 23, 66, 67, 76, 83, 84, 86, 87, 88, 89, 90, 92, 
            93, 94, 95, 99, 213, 220, 222, 262, 263, 264, 265, 267, 268, 269, 
            270, 271, 272, 273, 274, 275, 282, 285, 286, 287, 297, 298
        ])
        self.assertEqual(len(data), len(expected_product_ids_under_300))
        self.assertEqual(self._get_product_ids(data), expected_product_ids_under_300)

        for product in data:
            price = Decimal(product['list_price'])
            self.assertTrue(price <= Decimal('300.00'))

        # Khoảng giá không có sản phẩm nào
        response = self.client.get(reverse('product-list-create') + '?min_price=10000&max_price=11000')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 0)

        # min_price không hợp lệ
        response = self.client.get(reverse('product-list-create') + '?min_price=invalid')
        self.assertEqual(response.status_code, 400)
        self.assertIn('min_price phải là một số hợp lệ.', response.json()['error'])

        # max_price không hợp lệ
        response = self.client.get(reverse('product-list-create') + '?max_price=invalid')
        self.assertEqual(response.status_code, 400)
        self.assertIn('max_price phải là một số hợp lệ.', response.json()['error'])


    # --- Test case sắp xếp sản phẩm ---
    def test_sort_products(self):
        """
        Kiểm tra sắp xếp sản phẩm theo các tiêu chí khác nhau.
        """
        # Sắp xếp theo tên sản phẩm ASC
        response = self.client.get(reverse('product-list-create') + '?sort_by=product_name')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)

        product_names = [p['product_name'] for p in data]
        # Verify danh sách đã được sắp xếp theo thứ tự bảng chữ cái
        self.assertEqual(product_names, sorted(product_names))

        # Sắp xếp theo giá ASC
        response = self.client.get(reverse('product-list-create') + '?sort_by=list_price&order_by=asc')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)

        product_prices = [Decimal(p['list_price']) for p in data]
        self.assertEqual(product_prices, sorted(product_prices))

        # Sắp xếp theo giá DESC
        response = self.client.get(reverse('product-list-create') + '?sort_by=list_price&order_by=desc')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)

        product_prices = [Decimal(p['list_price']) for p in data]
        self.assertEqual(product_prices, sorted(product_prices, reverse=True))

        # Sắp xếp theo model_year DESC
        response = self.client.get(reverse('product-list-create') + '?sort_by=model_year&order_by=desc')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)

        product_model_years = [p['model_year'] for p in data]
        self.assertEqual(product_model_years, sorted(product_model_years, reverse=True))

        # Sắp xếp theo field không hợp lệ
        response = self.client.get(reverse('product-list-create') + '?sort_by=invalid_field')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Trường sắp xếp không hợp lệ.', response.json()['error'])

    # --- Test case kết hợp lọc và sắp xếp ---
    def test_filter_and_sort_combined(self):
        """
        Kiểm tra kết hợp lọc theo category_id, khoảng giá và sắp xếp theo tên.
        """
        # Lọc Mountain Bikes (category_id=6) có giá từ 1000 đến 3000, sắp xếp theo product_name ASC
        response = self.client.get(
            reverse('product-list-create') + '?category_id=6&min_price=1000&max_price=3000&sort_by=product_name'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)

        expected_combined_product_ids = sorted([
            4, 5, 8, 28, 31, 39, 41, 42, 46, 117, 120, 121, 122, 124, 128, 131, 132, 133, 134, 135, 136, 137, 138, 139, 141
        ])
        self.assertEqual(len(data), len(expected_combined_product_ids))

        # Kiểm tra lọc
        for product in data:
            self.assertEqual(product['category_name'], 'Mountain Bikes')
            price = Decimal(product['list_price'])
            self.assertTrue(Decimal('1000.00') <= price <= Decimal('3000.00'))

        # Kiểm tra sắp xếp
        actual_names = [p['product_name'] for p in data]
        self.assertEqual(actual_names, sorted(actual_names))

    def test_product_list_get(self):

        response = self.client.get(reverse('product-list-create'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        # Tổng số sản phẩm trong load_data_modified.sql là 321
        self.assertEqual(len(data), 321)
        
        # Verify dữ liệu của một sản phẩm cụ thể (sử dụng product_id=1 từ SQL)
        found_product = next((item for item in data if item['product_id'] == self.product_trek_820.product_id), None)
        self.assertIsNotNone(found_product)
        self.assertEqual(found_product['product_name'], 'Trek 820 - 2016')
        self.assertEqual(found_product['brand_name'], 'Trek')
        self.assertEqual(found_product['category_name'], 'Mountain Bikes')
        self.assertEqual(found_product['model_year'], 2016)
        self.assertEqual(found_product['list_price'], '379.99')

    def test_product_create_post_success(self):
        """
        Kiểm tra POST /api/production/products/ tạo mới thành công.
        """
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
        """
        Kiểm tra POST /api/production/products/ với các trường bắt buộc bị thiếu.
        """
        response = self.client.post(
            reverse('product-list-create'),
            data=json.dumps({'product_id': 999998, 'product_name': 'Incomplete Product'}), 
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
        self.assertIn('Thiếu trường bắt buộc', response.json()['error'])

    def test_product_create_post_duplicate_id(self):
        """
        Kiểm tra POST /api/production/products/ với product_id đã tồn tại.
        Expected trả về lỗi 409 Conflict.
        """
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
        """
        Kiểm tra POST /api/production/products/ với brand_id hoặc category_id không tồn tại.
        Expected trả về lỗi 404 Not Found.
        """
        # Kiểm tra brand_id không tồn tại
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

        # Kiểm tra category_id không tồn tại
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
        """
        Kiểm tra GET /api/production/products/<product_id>/ cho sản phẩm đã tồn tại.
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
        Kiểm tra GET /api/production/products/<product_id>/ cho sản phẩm không tồn tại.
        Expected trả về 404 Not Found.
        """
        response = self.client.get(reverse('product-detail', args=[999999])) # ID không tồn tại
        self.assertEqual(response.status_code, 404)
        self.assertIn('Sản phẩm không tồn tại', response.json()['error'])

    def test_product_update_patch_success(self):
        """
        Kiểm tra PATCH /api/production/products/<product_id>/ cập nhật thành công.
        """
        temp_product = Product.objects.create(
            product_id=999990, # Một ID duy nhất cho testcase nàyày
            product_name='Temporary Product For Update',
            brand_id=self.brand_electra,
            category_id=self.category_children,
            model_year=2020,
            list_price=Decimal('100.00')
        )

        update_data = {
            'product_name': 'Temporary Product - Updated Name',
            'list_price': '105.50',
            'category_id': self.category_road.category_id # Thay đổi Category
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
        self.assertEqual(response.json()['product_name'], 'Temporary Product - Updated Name')

        temp_product.delete()

    def test_product_update_patch_no_changes(self):
        """
        Kiểm tra PATCH /api/production/products/<product_id>/ khi không có thay đổi thực tế nào được thực hiện.
        Expected trả về 200 OK với dữ liệu hiện tại.
        """
        # Sử dụng một sản phẩm từ fixture cho việc này.
        original_name = self.product_trek_820.product_name
        original_price = self.product_trek_820.list_price

        response = self.client.patch(
            reverse('product-detail', args=[self.product_trek_820.product_id]),
            data=json.dumps({'product_name': original_name, 'list_price': str(original_price)}), # Dữ liệu giống nhau
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('product_id', response.json()) # Expected trả về dữ liệu hiện tại
        self.assertEqual(response.json()['product_name'], original_name)
        self.assertEqual(response.json()['list_price'], str(original_price))


    def test_product_update_patch_non_existent_product(self):
        """
        Kiểm tra PATCH /api/production/products/<product_id>/ cho sản phẩm không tồn tại.
        Expected trả về lỗi 404 Not Found.
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
        Kiểm tra PATCH /api/production/products/<product_id>/ với ID khóa ngoại không tồn tại.
        Expected trả về 404 Not Found cho đối tượng liên quan.
        """
        # Kiểm tra cập nhật với brand_id không tồn tại
        response = self.client.patch(
            reverse('product-detail', args=[self.product_trek_820.product_id]),
            data=json.dumps({'brand_id': 99999}), # ID Brand không tồn tại
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn('Brand với ID', response.json()['error'])

        # Kiểm tra cập nhật với category_id không tồn tại
        response = self.client.patch(
            reverse('product-detail', args=[self.product_trek_820.product_id]),
            data=json.dumps({'category_id': 99999}), # ID Category không tồn tại
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn('Category với ID', response.json()['error'])


    def test_product_delete_success(self):
        """
        Kiểm tra DELETE /api/production/products/<product_id>/ xóa thành công.
        """
        # Tạo một sản phẩm
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
        """
        Kiểm tra DELETE /api/production/products/<product_id>/ cho sản phẩm không tồn tại.
        Expected trả về 404 Not Found.
        """
        response = self.client.delete(reverse('product-detail', args=[999999])) # ID không tồn tại
        self.assertEqual(response.status_code, 404)
        self.assertIn('Sản phẩm không tồn tại', response.json()['error'])

    # --- Các bài kiểm tra cho Stock API ---
    def test_stock_list_get(self):
        """
        Kiểm tra endpoint GET /api/production/stocks/.
        Expected trả về danh sách tất cả các mục tồn kho.
        """
        response = self.client.get(reverse('stock-list-create'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), Stock.objects.count()) # Verify số lượng khớp với tổng số hàng tồn kho trong fixture

        # Verify dữ liệu của một mục tồn kho cụ thể (product_id=1, store_id=1)
        found_stock = next((item for item in data if item['product_id'] == self.product_trek_820.product_id and item['store_id'] == self.store_santa_cruz.store_id), None)
        self.assertIsNotNone(found_stock)
        # INSERT INTO stocks(store_id, product_id, quantity) VALUES(1,1,27);
        self.assertEqual(found_stock['quantity'], 27)
        self.assertEqual(found_stock['store_name'], 'Santa Cruz Bikes')
        self.assertEqual(found_stock['product_name'], 'Trek 820 - 2016')

    def test_stock_create_post_success(self):
        """
        Kiểm tra POST /api/production/stocks/ tạo mới thành công.
        Sử dụng một cặp (store_id, product_id) mới.
        """
        initial_stock_count = Stock.objects.count()

        # Tạo một sản phẩm và cửa hàng chưa có fixture

        temp_product = Product.objects.create(
            product_id=999999, 
            product_name='Ephemeral Test Product',
            brand_id=self.brand_electra, #Brand đã tồn tại
            category_id=self.category_children, #Category đã tồn tại
            model_year=2025,
            list_price=Decimal('10.00')
        )
        temp_store = Store.objects.create(
            store_id=999999, 
            store_name='Ephemeral Test Store',
            city='TestCity', district='TC', zip_code='11111'
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
        self.assertEqual(response.status_code, 201) # 201 Đã tạo
        self.assertEqual(Stock.objects.count(), initial_stock_count + 1)
        self.assertEqual(response.json()['quantity'], 75)
        self.assertTrue(Stock.objects.filter(
            store_id=temp_store,
            product_id=temp_product,
            quantity=75
        ).exists())

        # Dọn dẹp các đối tượng tạm thời
        Stock.objects.get(store_id=temp_store, product_id=temp_product).delete()
        temp_product.delete()
        temp_store.delete()

    def test_stock_create_post_missing_field(self):
        """
        Kiểm tra POST /api/production/stocks/ với các field bắt buộc bị thiếu (ví dụ: quantity).
        """
        response = self.client.post(
            reverse('stock-list-create'),
            data=json.dumps({'store_id': self.store_santa_cruz.store_id, 'product_id': self.product_trek_820.product_id}), # Thiếu số lượng
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
        self.assertIn('Thiếu trường bắt buộc', response.json()['error'])

    def test_stock_create_post_duplicate_entry(self):
        """
        Kiểm tra POST /api/production/stocks/ với cặp (store_id, product_id) đã tồn tại.
        Expected trả về 409 Conflict do ràng buộc unique_together.
        """
        # Sử dụng (store_id=1, product_id=1) là (Santa Cruz, Trek 820) đã tồn tại trong fixture
        response = self.client.post(
            reverse('stock-list-create'),
            data=json.dumps({'store_id': self.store_santa_cruz.store_id,
                             'product_id': self.product_trek_820.product_id,
                             'quantity': 10}), # Cố tình tạo bản sao của kho hiện có
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 409) # conflict
        self.assertIn('đã tồn tại', response.json()['error'])
        self.assertIn('Bản ghi tồn kho cho sản phẩm này tại cửa hàng này đã tồn tại', response.json()['error'])

    def test_stock_create_post_non_existent_foreign_key(self):
        """
        Kiểm tra POST /api/production/stocks/ với store_id hoặc product_id không tồn tại.
        Expected trả về 404 Not Found.
        """
        # Kiểm tra với store_id không tồn tại
        response = self.client.post(
            reverse('stock-list-create'),
            data=json.dumps({'store_id': 999999, # ID cửa hàng không tồn tại
                             'product_id': self.product_trek_820.product_id,
                             'quantity': 10}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn('Cửa hàng với ID', response.json()['error'])

        # Kiểm tra với product_id không tồn tại
        response = self.client.post(
            reverse('stock-list-create'),
            data=json.dumps({'store_id': self.store_santa_cruz.store_id,
                             'product_id': 999999, # ID sản phẩm không tồn tại
                             'quantity': 10}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn('Sản phẩm với ID', response.json()['error'])

    def test_stock_detail_get_success(self):
        """
        Kiểm tra GET /api/production/stocks/<store_id>/<product_id>/ cho kho đã tồn tại.
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
        Kiểm tra GET /api/production/stocks/<store_id>/<product_id>/ cho kho không tồn tại.
        Expected trả về 404 Not Found.
        """
        # Sản phẩm không tồn tại tại cửa hàng hiện có
        response = self.client.get(reverse('stock-detail', args=[self.store_santa_cruz.store_id, 999999]))
        self.assertEqual(response.status_code, 404)
        self.assertIn('Bản ghi tồn kho không tồn tại', response.json()['error'])

        # Cửa hàng không tồn tại cho sản phẩm hiện có
        response = self.client.get(reverse('stock-detail', args=[999999, self.product_trek_820.product_id]))
        self.assertEqual(response.status_code, 404)
        self.assertIn('Bản ghi tồn kho không tồn tại', response.json()['error'])

    def test_stock_update_patch_success(self):
        """
        Kiểm tra PATCH /api/production/stocks/<store_id>/<product_id>/ cập nhật thành công.
        """
        # Tạo một mục tồn kho mới
        temp_stock_product = Product.objects.create(
            product_id=999980, product_name='Update Test Product', brand_id=self.brand_electra, category_id=self.category_children, model_year=2020, list_price=Decimal('100.00')
        )
        temp_stock_store = Store.objects.create(
            store_id=999980, store_name='Update Test Store', city='UCity', district='UT', zip_code='00000'
        )
        temp_stock = Stock.objects.create(store_id=temp_stock_store, product_id=temp_stock_product, quantity=50)

        new_quantity = 15

        update_data = {
            'quantity': new_quantity
        }
        response = self.client.patch(
            reverse('stock-detail', args=[temp_stock.store_id.store_id, temp_stock.product_id.product_id]),
            data=json.dumps(update_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        temp_stock.refresh_from_db()
        self.assertEqual(temp_stock.quantity, new_quantity)
        self.assertEqual(response.json()['quantity'], new_quantity)

        temp_stock.delete()
        temp_stock_product.delete()
        temp_stock_store.delete()


    def test_stock_update_patch_no_changes(self):
        """
        Kiểm tra PATCH /api/production/stocks/<store_id>/<product_id>/ khi không có thay đổi thực tế nào được thực hiện.
        Expected trả về 200 OK với một thông báo cụ thể.
        """
        # Lấy một mục tồn kho từ fixture
        current_quantity = self.stock_trek_820_santa_cruz.quantity
        response = self.client.patch(
            reverse('stock-detail', args=[self.stock_trek_820_santa_cruz.store_id.store_id, self.stock_trek_820_santa_cruz.product_id.product_id]),
            data=json.dumps({'quantity': current_quantity}), # Dữ liệu giống nhau
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('Không có thay đổi nào được thực hiện', response.json()['message'])

    def test_stock_update_patch_non_existent_stock(self):
        """
        Kiểm tra PATCH /api/production/stocks/<store_id>/<product_id>/ cho kho không tồn tại.
        Expected trả về 404 Not Found.
        """
        response = self.client.patch(
            reverse('stock-detail', args=[999999, 999999]), # Cặp không tồn tại
            data=json.dumps({'quantity': 5}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn('Bản ghi tồn kho không tồn tại', response.json()['error'])

    def test_stock_update_patch_missing_quantity_field(self):
        """
        Kiểm tra PATCH /api/production/stocks/<store_id>/<product_id>/ với trường quantity bị thiếu.
        """
        response = self.client.patch(
            reverse('stock-detail', args=[self.stock_trek_820_santa_cruz.store_id.store_id, self.stock_trek_820_santa_cruz.product_id.product_id]),
            data=json.dumps({'some_other_field': 'value'}), # Thiếu số lượng
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('Thiếu trường bắt buộc: quantity', response.json()['error'])

    def test_stock_delete_success(self):
        """
        Kiểm tra DELETE /api/production/stocks/<store_id>/<product_id>/ xóa thành công.
        """
        # Tạo một mục tồn kho
        temp_delete_product = Product.objects.create(
            product_id=999970, product_name='Delete Test Product', brand_id=self.brand_haro, category_id=self.category_road, model_year=2021, list_price=Decimal('500.00')
        )
        temp_delete_store = Store.objects.create(
            store_id=999970, store_name='Delete Test Store', city='DCity', district='DT', zip_code='22222'
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
        """
        Kiểm tra DELETE /api/production/stocks/<store_id>/<product_id>/ cho kho không tồn tại.
        Expected trả về 404 Not Found.
        """
        response = self.client.delete(reverse('stock-detail', args=[999999, 999999])) # Cặp không tồn tại
        self.assertEqual(response.status_code, 404)
        self.assertIn('Bản ghi tồn kho không tồn tại', response.json()['error'])
        
class ProductionAdminTests(TestCase):
    """
    Test case cho production/admin.py.
    TTạo một superuser, đăng nhập và kiểm tra nội dung HTML của các trang danh sách thay đổi trong admin.
    """
    fixtures = ['production_initial_data']

    @classmethod
    def setUpTestData(cls):
        """
        Tạo một superuser để sử dụng cho tất cả các test trong class này.
        """
        super().setUpTestData()
        cls.admin_user = User.objects.create_superuser(
            username='admin_test',
            email='admin_test@example.com',
            password='12345678'
        )
    
    def setUp(self):
        """
        Đăng nhập với superuser trước mỗi lần chạy test.
        """
        self.client = Client()
        self.client.login(username='admin_test', password='12345678')

    # --- Test case cho BrandAdmin ---
    def test_brand_admin_list_view(self):
        """
        Kiểm tra trang danh sách Brand: list_display và ordering.
        """
        url = reverse('admin:production_brand_changelist')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # 1. Kiểm tra các cột (list_display)
        self.assertContains(response, 'Brand id')
        self.assertContains(response, 'Brand name')
        
        # 2. Kiểm tra ordering theo 'brand_name'
        content = response.content.decode('utf-8')
        pos_electra = content.find('Electra')
        pos_trek = content.find('Trek')
        self.assertTrue(pos_electra > 0 and pos_trek > 0, "Brand names not found in response")
        self.assertTrue(pos_electra < pos_trek, "Brands are not ordered by name correctly")

    def test_brand_admin_search(self):
        """
        Kiểm tra ô tìm kiếm của BrandAdmin (search_fields).
        """
        url = reverse('admin:production_brand_changelist')
        response = self.client.get(url, {'q': 'Haro'}, follow=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Haro')
        self.assertNotContains(response, 'Trek')

    # --- Các bài kiểm tra cho CategoryAdmin ---
    def test_category_admin_list_view(self):
        """
        Kiểm tra trang danh sách Category: list_display và ordering.
        """
        url = reverse('admin:production_category_changelist')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Category id')
        self.assertContains(response, 'Category name')
        
        content = response.content.decode('utf-8')
        pos_comfort = content.find('Comfort Bicycles')
        pos_road = content.find('Road Bikes')
        self.assertTrue(pos_comfort > 0 and pos_road > 0, "Category names not found")
        self.assertTrue(pos_comfort < pos_road, "Categories are not ordered by name correctly")

    def test_category_admin_search(self):
        """
        Kiểm tra ô tìm kiếm của CategoryAdmin (search_fields).
        """
        url = reverse('admin:production_category_changelist')
        
        response = self.client.get(url, {'q': 'Mountain'}, follow=True)
        
        # Bây giờ status_code sẽ là 200 của trang kết quả cuối cùng
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Mountain Bikes')
        self.assertNotContains(response, 'Road Bikes')

    #--- Các bài kiểm tra cho StockAdmin ---
    def test_stock_admin_list_view(self):
        """
        Kiểm tra trang danh sách Stock: list_display và các phương thức tùy chỉnh.
        """
        url = reverse('admin:production_stock_changelist')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Kiểm tra các header của cột được định nghĩa trong @admin.display
        self.assertContains(response, 'Product Name')
        self.assertContains(response, 'Store Name')
        self.assertContains(response, 'Quantity')

        # Kiểm tra dữ liệu từ khóa ngoại được hiển thị
        self.assertContains(response, 'Electra Cruiser Lux 1 - 2017') # Tên sản phẩm
        self.assertContains(response, 'Santa Cruz Bikes') # Tên cửa hàng

    def test_stock_admin_search(self):
        """
        Kiểm tra ô tìm kiếm của StockAdmin (search_fields với __ lookup).
        """
        url = reverse('admin:production_stock_changelist')
        
        # Tìm theo tên sản phẩm
        response = self.client.get(url, {'q': 'Trek 820'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Trek 820 - 2016')
        self.assertNotContains(response, 'Ritchey Timberwolf')

        # Tìm theo tên cửa hàng
        response = self.client.get(url, {'q': 'Baldwin'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Baldwin Bikes')
        self.assertNotContains(response, 'Santa Cruz Bikes')

    def test_stock_admin_filter_by_store(self):
        """
        Kiểm tra bộ lọc của StockAdmin (list_filter).
        """
        store_to_filter = Store.objects.get(store_name='Rowlett Bikes')
        url = reverse('admin:production_stock_changelist')
        
        # Lọc theo store_id
        response = self.client.get(url, {'store_id__store_id__exact': store_to_filter.pk})
        self.assertEqual(response.status_code, 200)

        # Kết quả chỉ nên chứa cửa hàng 'Rowlett Bikes'
        self.assertContains(response, 'Rowlett Bikes')
        self.assertNotContains(response, 'Santa Cruz Bikes')