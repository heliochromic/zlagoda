from django.contrib import admin

# Register your models here.
from .models import Employee, Category, Product, Store_Product, Check, Sale, Customer_Card

admin.site.register(Employee)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Store_Product)
admin.site.register(Check)
admin.site.register(Sale)
admin.site.register(Customer_Card)
