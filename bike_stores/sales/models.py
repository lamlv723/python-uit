from django.db import models
from .fields import IntegerDateField

class Customer(models.Model):
    customer_id = models.IntegerField(primary_key=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    phone = models.CharField(max_length=25, null=True, blank=True)
    street = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=25, null=True, blank=True)
    zip_code = models.CharField(max_length=11, null=True, blank=True)

    class Meta:
        db_table = 'customers'

class Store(models.Model):
    store_id = models.IntegerField(primary_key=True)
    store_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=25, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    street = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=10, null=True, blank=True)
    zip_code = models.CharField(max_length=5, null=True, blank=True)

    class Meta:
        db_table = 'stores'

class Staff(models.Model):
    staff_id = models.IntegerField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.CharField(max_length=255, unique=True)
    phone = models.CharField(max_length=25, null=True, blank=True)
    active = models.BooleanField()
    store_id = models.ForeignKey(Store, db_column='store_id', on_delete=models.CASCADE)
    manager_id = models.ForeignKey('self', db_column='manager_id', null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = 'staffs'

class Order(models.Model):
    order_id = models.IntegerField(primary_key=True)
    ORDER_STATUS_CHOICES = [
        (1, 'Pending'),
        (2, 'Processing'),
        (3, 'Rejected'),
        (4, 'Completed'),
    ]
    customer_id = models.ForeignKey(Customer, db_column='customer_id', on_delete=models.CASCADE, null=True, blank=True)
    order_status = models.PositiveSmallIntegerField(choices=ORDER_STATUS_CHOICES)
    order_date = IntegerDateField()
    required_date = IntegerDateField()
    shipped_date = IntegerDateField(null=True, blank=True)
    store_id = models.ForeignKey(Store, db_column='store_id', on_delete=models.CASCADE)
    staff_id = models.ForeignKey(Staff, db_column='staff_id', on_delete=models.PROTECT)

    class Meta:
        db_table = 'orders'

class OrderItem(models.Model):
    order_id = models.ForeignKey(Order, db_column='order_id', on_delete=models.CASCADE)
    item_id = models.PositiveIntegerField()
    product_id = models.ForeignKey('production.Product', db_column='product_id', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    list_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=4, decimal_places=2, default=0)

    class Meta:
        unique_together = ('order_id', 'item_id')
        db_table = 'order_items'
