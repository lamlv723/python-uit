from django.db import models
from sales.models import Store
from products.models import Product

class Stock(models.Model):
    store_id = models.ForeignKey(Store, db_column='store_id', on_delete=models.CASCADE)
    product_id = models.ForeignKey(Product, db_column='product_id', on_delete=models.CASCADE)
    quantity = models.IntegerField()

    class Meta:
        unique_together = ('store_id', 'product_id')
        db_table = 'stocks'
