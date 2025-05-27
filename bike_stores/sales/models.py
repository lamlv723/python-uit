from django.db import models
from products.models import Product

class Customer(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=25, null=True, blank=True)
    email = models.CharField(max_length=255)
    street = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=25, null=True, blank=True)
    zip_code = models.CharField(max_length=5, null=True, blank=True)

class Store(models.Model):
    store_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=25, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    street = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=10, null=True, blank=True)
    zip_code = models.CharField(max_length=5, null=True, blank=True)

class Staff(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.CharField(max_length=255, unique=True)
    phone = models.CharField(max_length=25, null=True, blank=True)
    active = models.BooleanField()
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    manager = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)

class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        (1, 'Pending'),
        (2, 'Processing'),
        (3, 'Rejected'),
        (4, 'Completed'),
    ]
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    order_status = models.PositiveSmallIntegerField(choices=ORDER_STATUS_CHOICES)
    order_date = models.DateField()
    required_date = models.DateField()
    shipped_date = models.DateField(null=True, blank=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    staff = models.ForeignKey(Staff, on_delete=models.PROTECT)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    item_id = models.PositiveIntegerField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    list_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=4, decimal_places=2, default=0)

    class Meta:
        unique_together = ('order', 'item_id')
