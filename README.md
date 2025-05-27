# Đồ án cuối kỳ môn Kỹ thuật lập trình Python
## Bike Stores - Python Django Project

Đồ Django này là một ví dụ triển khai cơ sở dữ liệu BikeStores, ban đầu được thiết kế cho các bài học SQL Server. Dự án sử dụng cơ sở dữ liệu mặc định SQLite của Django và bao gồm nhiều app: `products`, `sales`, và `inventory`, mỗi app chứa các model liên quan.

## Bắt đầu

Làm theo các bước sau để thiết lập dự án trên máy của bạn:

### 1. Clone repository

```bash
git clone https://github.com/ten-ban/bike_stores.git
cd bike_stores
```

### 2. Tạo môi trường ảo (khuyến nghị)

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Cài đặt thư viện phụ thuộc

Nếu có file `requirements.txt`:

```bash
pip install -r requirements.txt
```

Hoặc cài Django thủ công:

```bash
pip install django
```

### 4. Chạy migrate để tạo cơ sở dữ liệu

Django sẽ tạo các bảng dựa trên các file migration đã có:

```bash
python3 manage.py migrate
```

### 5. Tạo tài khoản superuser

Tài khoản này dùng để truy cập vào trang quản trị của Django:

```bash
python3 manage.py createsuperuser
```

### 6. Chạy server phát triển

```bash
python3 manage.py runserver
```

Truy cập trang admin tại: [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)

## Lưu ý

* File `db.sqlite3` đã được thêm vào `.gitignore` nên sẽ không bị đẩy lên Git.
* Cấu trúc cơ sở dữ liệu sẽ được tạo lại từ các file migration, không cần file `.sqlite3` có sẵn.
* Nếu cần dữ liệu mẫu, bạn có thể import bằng fixture hoặc script riêng.

## Cấu trúc các app

* `products`: quản lý các model liên quan đến sản phẩm như `Category`, `Brand`, `Product`.
* `sales`: chứa các model về khách hàng, nhân viên, cửa hàng và đơn hàng.
* `inventory`: quản lý tồn kho giữa sản phẩm và cửa hàng.

---

Bạn có thể fork và mở rộng dự án này cho việc học hoặc mục đích sản xuất.
