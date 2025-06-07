from django.db import models
from datetime import date


class IntegerDateField(models.DateField):
    description = "Một trường ngày tháng được lưu trữ dưới dạng số nguyên (YYYYMMDD)"

    def get_internal_type(self):
        # Báo cho Django biết rằng kiểu dữ liệu thực sự trong CSDL là Integer
        return "IntegerField"

    def from_db_value(self, value, expression, connection):
        # Được gọi khi đọc dữ liệu TỪ CSDL
        # Chuyển đổi integer (ví dụ: 20240608) thành object date của Python
        if value is None:
            return None
        try:
            value_str = str(value)
            return date(
                year=int(value_str[0:4]),
                month=int(value_str[4:6]),
                day=int(value_str[6:8])
            )
        except (ValueError, TypeError):
            return None

    def to_python(self, value):
        # Được gọi trong các quá trình khác như deserialization
        if isinstance(value, date):
            return value
        if value is None:
            return None
        return self.from_db_value(value, None, None)

    def get_prep_value(self, value):
        # Được gọi khi chuẩn bị ghi dữ liệu VÀO CSDL
        # Chuyển đổi object date của Python thành integer (YYYYMMDD)
        if value is None:
            return None
        if isinstance(value, str):
            value = date.fromisoformat(value)  # Chuyển đổi nếu nhận vào string

        return int(value.strftime('%Y%m%d'))