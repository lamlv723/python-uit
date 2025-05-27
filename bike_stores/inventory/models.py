from django.db import models
from sales.models import Store
from products.models import Product

class Stock(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    class Meta:
        unique_together = ('store', 'product')
        db_table = 'stocks'
