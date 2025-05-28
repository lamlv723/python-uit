from django.db import models

class Category(models.Model):
    category_id = models.IntegerField(primary_key=True)
    category_name = models.CharField(max_length=255)

    class Meta:
        db_table = 'categories'

class Brand(models.Model):
    brand_id = models.IntegerField(primary_key=True)
    brand_name = models.CharField(max_length=255)

    class Meta:
        db_table = 'brands'

class Product(models.Model):
    product_id = models.IntegerField(primary_key=True)
    product_name = models.CharField(max_length=255)
    brand_id = models.ForeignKey(Brand, db_column='brand_id', on_delete=models.CASCADE)
    category_id = models.ForeignKey(Category, db_column='category_id', on_delete=models.CASCADE)
    model_year = models.SmallIntegerField()
    list_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'products'

class Stock(models.Model):
    store_id = models.ForeignKey('sales.Store', db_column='store_id', on_delete=models.CASCADE)
    product_id = models.ForeignKey(Product, db_column='product_id', on_delete=models.CASCADE)
    quantity = models.IntegerField()

    class Meta:
        unique_together = ('store_id', 'product_id')
        db_table = 'stocks'