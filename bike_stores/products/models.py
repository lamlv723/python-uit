from django.db import models

class Category(models.Model):
    category_name = models.CharField(max_length=255)

class Brand(models.Model):
    brand_name = models.CharField(max_length=255)

class Product(models.Model):
    product_name = models.CharField(max_length=255)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    model_year = models.SmallIntegerField()
    list_price = models.DecimalField(max_digits=10, decimal_places=2)
