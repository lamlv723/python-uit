from django.contrib import admin
from .models import Customer, Store, Staff, Order, OrderItem

admin.site.register(Customer)
admin.site.register(Store)
admin.site.register(Staff)
admin.site.register(Order)
admin.site.register(OrderItem)
