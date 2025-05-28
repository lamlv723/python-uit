# Đồ án cuối kỳ môn Kỹ thuật lập trình Python

## Bike Stores - Python Django Project

Dự án Django này là một ví dụ triển khai cơ sở dữ liệu [BikeStores](http://127.0.0.1:8000/), ban đầu được thiết kế cho các bài học SQL Server. Dự án sử dụng cơ sở dữ liệu mặc định SQLite của Django và bao gồm nhiều app: `products`, `sales`, và `inventory`, mỗi app chứa các model liên quan.

## Bắt đầu

Làm theo các bước sau để thiết lập dự án trên máy của bạn:

### 1. Clone repository

```bash
git clone https://github.com/ten-ban/bike_stores.git
cd bike_stores
```

### 2. Tạo môi trường ảo (khuyến nghị)

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Cài đặt thư viện cần thiết (cài vào venv)

Sau khi activate virtual environment, cài đặt thư viện trong file `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 4. Chạy server phát triển

```bash
python manage.py runserver
```

* Truy cập trang chủ tại: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
* Truy cập trang admin tại: [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)

### 5. Tài khoản superuser

* Username: `admin`
* Password: `12345678`

## Cấu trúc các app

### `production`

Quản lý các model liên quan đến sản phẩm:

* `Category`:

  * `category_id`
  * `category_name`
* `Brand`:

  * `brand_id`
  * `brand_name`
* `Product`:

  * `product_id`
  * `product_name`
  * `brand_id` (FK → `Brand`)
  * `category_id` (FK → `Category`)
  * `model_year`
  * `list_price`

* `Stock`:

  * `store_id` (FK → `Store`)
  * `product_id` (FK → `Product`)
  * `quantity`
  * **Primary key**: (`store_id`, `product_id`)
### `sales`

Quản lý khách hàng, nhân viên, cửa hàng và đơn hàng:

* `Customer`:

  * `customer_id`
  * `first_name`, `last_name`, `phone`, `email`
  * `street`, `city`, `state`, `zip_code`
* `Store`:

  * `store_id`
  * `store_name`, `phone`, `email`
  * `street`, `city`, `state`, `zip_code`
* `Staff`:

  * `staff_id`
  * `first_name`, `last_name`, `email`, `phone`
  * `active`
  * `store_id` (FK → `Store`)
  * `manager_id` (FK → chính `Staff`)
* `Order`:

  * `order_id`
  * `customer_id` (FK → `Customer`)
  * `order_status` (1=Pending, 2=Processing, 3=Rejected, 4=Completed)
  * `order_date`, `required_date`, `shipped_date`
  * `store_id` (FK → `Store`)
  * `staff_id` (FK → `Staff`)
* `OrderItem`:

  * `order_id` (FK → `Order`)
  * `item_id`
  * `product_id` (FK → `Product`)
  * `quantity`
  * `list_price`
  * `discount`
  * **Primary key**: (`order_id`, `item_id`)

## Misc
```bash
rm db.sqlite3
rm production/migrations/00*.py
rm sales/migrations/00*.py


python3 manage.py makemigrations
python3 manage.py migrate

python3 manage.py createsuperuser

sqlite3 db.sqlite3 < load_data_modified.sql
```