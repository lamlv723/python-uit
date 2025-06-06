# Đồ án cuối kỳ môn Kỹ thuật lập trình Python

## Bike Stores - Python Django Project

Dự án Django này là một ví dụ triển khai cơ sở dữ liệu [BikeStores](https://www.sqlservertutorial.net/getting-started/sql-server-sample-database/), ban đầu được thiết kế cho các bài học SQL Server. Dự án sử dụng cơ sở dữ liệu mặc định SQLite của Django và bao gồm các app: `production` và `sales`. Mỗi app chứa các model liên quan.

---

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

### 3.1. Tạo file cấu hình môi trường `.env`

Sao chép file mẫu `.env.example` thành `.env`:

```bash
copy .env.example .env   # Windows
```

hoặc

```bash
cp .env.example .env     # Linux/macOS
```

### 4. Chạy server phát triển

```bash
python manage.py runserver
```

- Truy cập trang chủ tại: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- Truy cập trang admin tại: [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)

### 4.1. Chạy test tự động

Để kiểm tra các chức năng của dự án, bạn có thể chạy toàn bộ test bằng lệnh:

```bash
python manage.py test
```

### 5. Tài khoản superuser

- Username: `admin`
- Password: `12345678`

---

## Truy cập Cơ sở dữ liệu (SQLite3)

Bạn có thể truy vấn trực tiếp cơ sở dữ liệu `db.sqlite3` bằng công cụ dòng lệnh `sqlite3`.

1.  **Mở terminal của bạn và di chuyển đến thư mục gốc của dự án** (nơi chứa file `manage.py` và `db.sqlite3`).
    Ví dụ:

    ```bash
    cd path/to/bike_stores
    ```

2.  **Kết nối với cơ sở dữ liệu:**

    ```bash
    sqlite3 db.sqlite3
    ```

    Lệnh này sẽ mở dấu nhắc của SQLite (`sqlite>`).

3.  **Hiển thị các bảng có sẵn:**

    ```sqlite
    .tables

    ```

4.  **Chạy một truy vấn đơn giản:**
    Để chọn tất cả dữ liệu từ một bảng (ví dụ: một bảng có tên `customers` hoặc tên bảng cụ thể của bạn như `production_customer`):

    ```sqlite
    SELECT * FROM customers;
    ```

    **Lưu ý quan trọng:** Tất cả các câu lệnh truy vấn SQL **phải** kết thúc bằng dấu chấm phẩy (`;`) để chúng có thể thực thi trong `sqlite3`. Nếu bạn nhấn Enter mà không có dấu chấm phẩy, trình bao thường sẽ hiển thị dấu nhắc tiếp tục (như `...>`) để chờ bạn hoàn thành lệnh.

5.  **Thoát khỏi SQLite:**
    ```sqlite
    .quit
    ```

**Lưu ý:** Nếu lệnh `.tables` không hiển thị gì hoặc các bảng của ứng dụng Django bị thiếu, có thể bạn cần chạy Django migrations trước:

```bash
python manage.py makemigrations
python manage.py migrate
```

## Cấu trúc các app

### `production`

Quản lý các model liên quan đến sản phẩm:

- `Category`:

  - `category_id`
  - `category_name`

- `Brand`:

  - `brand_id`
  - `brand_name`

- `Product`:

  - `product_id`
  - `product_name`
  - `brand_id` (FK → `Brand`)
  - `category_id` (FK → `Category`)
  - `model_year`
  - `list_price`

- `Stock`:

  - `store_id` (FK → `Store`)
  - `product_id` (FK → `Product`)
  - `quantity`
  - **Primary key**: (`store_id`, `product_id`)

### `sales`

Quản lý khách hàng, nhân viên, cửa hàng và đơn hàng:

- `Customer`:

  - `customer_id`
  - `first_name`, `last_name`, `phone`, `email`
  - `street`, `city`, `state`, `zip_code`

- `Store`:

  - `store_id`
  - `store_name`, `phone`, `email`
  - `street`, `city`, `state`, `zip_code`

- `Staff`:

  - `staff_id`
  - `first_name`, `last_name`, `email`, `phone`
  - `active`
  - `store_id` (FK → `Store`)
  - `manager_id` (FK → chính `Staff`)

- `Order`:

  - `order_id`
  - `customer_id` (FK → `Customer`)
  - `order_status` (1=Pending, 2=Processing, 3=Rejected, 4=Completed)
  - `order_date`, `required_date`, `shipped_date`
  - `store_id` (FK → `Store`)
  - `staff_id` (FK → `Staff`)

- `OrderItem`:

  - `order_id` (FK → `Order`)
  - `item_id`
  - `product_id` (FK → `Product`)
  - `quantity`
  - `list_price`
  - `discount`
  - **Primary key**: (`order_id`, `item_id`)

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

```

```
