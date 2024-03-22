from django.db import models


# Create your models here.

class Employee(models.Model):
    id_employee = models.CharField(max_length=10, primary_key=True, help_text="Enter employee id")
    empl_surname = models.CharField(max_length=50, help_text="Enter employee surname")
    empl_name = models.CharField(max_length=50, help_text="Enter employee name")
    empl_patronymic = models.CharField(max_length=50, null=True, help_text="Enter employee patronymic")
    empl_role = models.CharField(max_length=10, help_text="Enter employee role")
    salary = models.DecimalField(max_digits=14, decimal_places=4, help_text="Enter employee salary")
    date_of_birth = models.DateField(help_text="Enter employee date of birth")
    date_of_start = models.DateField(help_text="Enter date of employee work started")
    phone_number = models.CharField(max_length=13, help_text="Enter employee phone_number")
    city = models.CharField(max_length=50, help_text="Enter employee city")
    street = models.CharField(max_length=50, help_text="Enter employee street")
    zip_code = models.CharField(max_length=9, help_text="Enter employee zip code")


class Category(models.Model):
    category_number = models.AutoField(primary_key=True, help_text="Enter category id")
    category_name = models.CharField(max_length=50, help_text="Enter category name")


class Product(models.Model):
    id_product = models.AutoField(primary_key=True, help_text="Enter product id")
    category_number = models.ForeignKey(Category, on_delete=models.DO_NOTHING, related_name="products")
    product_name = models.CharField(max_length=50, help_text="Enter product name")
    characteristics = models.TextField(max_length=100, help_text="Enter product characteristics")


class Store_Product(models.Model):
    UPC = models.CharField(max_length=12, primary_key=True, help_text="Enter store product's UPC")
    UPC_prom = models.ForeignKey('self', on_delete=models.SET_NULL, null=True,
                                 help_text="Enter store product's promotion UPC")
    id_product = models.ForeignKey(Product, on_delete=models.DO_NOTHING, related_name="products",
                                   help_text="Enter store product's id")
    selling_price = models.DecimalField(max_digits=13, decimal_places=4, help_text="Enter store product's price")
    products_number = models.IntegerField(help_text="Enter number of store products")
    promotional_product = models.BooleanField(help_text="Is store product on discount")


class Customer_Card(models.Model):
    card_number = models.CharField(max_length=13, primary_key=True, help_text="Enter customer card number")
    cust_surname = models.CharField(max_length=50, help_text="Enter customer surname")
    cust_name = models.CharField(max_length=50, help_text="Enter customer name")
    cust_patronymic = models.CharField(max_length=50, null=True,  help_text="Enter customer patronymic")
    phone_number = models.CharField(max_length=13, help_text="Enter customer phone number")
    city = models.CharField(max_length=50, null=True, help_text="Enter customer city")
    street = models.CharField(max_length=50, null=True, help_text="Enter customer street")
    zip_code = models.CharField(max_length=9, null=True, help_text="Enter customer zip code")
    percent = models.IntegerField(help_text="Enter customer discount")


class Check(models.Model):
    check_number = models.CharField(max_length=10, primary_key=True, help_text="Enter receipt's number")
    id_employee = models.ForeignKey(Employee, on_delete=models.DO_NOTHING, related_name="receipts",
                                    help_text="Enter id of employee who issued receipt")
    card_number = models.ForeignKey(Customer_Card, on_delete=models.DO_NOTHING,
                                    null=True, related_name="receipts",
                                    help_text="Enter card number associated with receipt")
    print_date = models.DateTimeField(help_text="Enter receipt's print date")
    sum_total = models.DecimalField(max_digits=13, decimal_places=4, help_text="Enter receipt's total sum")
    vat = models.DecimalField(max_digits=13, decimal_places=4, help_text="Enter receipt's vat")


class Sale(models.Model):
    UPC = models.ForeignKey(Store_Product, on_delete=models.DO_NOTHING, related_name="sold",
                            help_text="Enter product's UPC", primary_key=True)
    check_number = models.ForeignKey(Check, on_delete=models.CASCADE,
                                     related_name="products", help_text="Enter number of receipt")
    product_number = models.IntegerField(help_text="Enter number of units sold")
    selling_price = models.DecimalField(max_digits=13, decimal_places=4, help_text="Enter selling price per unit")
