import re

from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import ValidationError
from django.db import connection

from .models import Category, Employee, Product, Store_Product


class ProductFilterForm(forms.Form):
    product_name = forms.CharField(label='Search', max_length=100, required=False)
    category_name = forms.ModelChoiceField(queryset=Category.objects.all(), empty_label='All Categories',
                                           required=False)


class ProductDetailForm(forms.Form):
    product_name = forms.CharField(label='Product Name', max_length=100)
    characteristics = forms.CharField(label='Characteristics', widget=forms.Textarea)
    category = forms.ModelChoiceField(queryset=Category.objects.all(), label='Category', empty_label='All Categories')


class StoreProductFilterForm(forms.Form):
    product_upc = forms.CharField(label='Product UPC', max_length=12,
                                  widget=forms.TextInput(attrs={'placeholder': "Enter store product's UPC"}),
                                  required=False)
    discount_available = forms.BooleanField(label='Only discount products', required=False)
    discount_unavailable = forms.BooleanField(label='Only full price products', required=False)
    sort_by_name = forms.BooleanField(label='Sort by name', required=False)
    sort_by_quantity = forms.BooleanField(label='Sort by quantity', required=False)


class StoreProductDetailForm(forms.Form):
    product_upc = forms.CharField(label='Product UPC', max_length=12,
                                  widget=forms.TextInput(attrs={'placeholder': "Enter store product's UPC"}))
    selling_price = forms.DecimalField(label='Selling price', max_digits=13, decimal_places=4)
    products_number = forms.DecimalField(label='Product number')
    id_product_id = forms.ModelChoiceField(queryset=Product.objects.all(), label='id product')


class StorePromotionalProductDetailForm(forms.Form):
    product_upc = forms.CharField(label='Product UPC', max_length=12,
                                  widget=forms.TextInput(attrs={'placeholder': "Enter store product's UPC"}))
    products_number = forms.DecimalField(label='Product number')


class StorePromotionalProductUpdateForm(forms.Form):
    products_number = forms.DecimalField(label='Product number')


class EmployeeFilterForm(forms.Form):
    employee_name = forms.CharField(label='Search', max_length=100, required=False)
    empl_role_choices = Employee.objects.values_list('empl_role', flat=True).distinct()
    empl_role_choices = [(role, role) for role in empl_role_choices]
    empl_role_choices.insert(0, ('', 'All Roles'))

    employee_role = forms.ChoiceField(choices=empl_role_choices, required=False)


class EmployeeDetailForm(forms.Form):
    id_employee = forms.CharField(max_length=10, help_text="Enter employee id")
    employee_name = forms.CharField(max_length=50, help_text="Enter employee name")
    employee_surname = forms.CharField(max_length=50, help_text="Enter employee surname")
    employee_patronymic = forms.CharField(max_length=50, required=False,
                                          help_text="Enter patronymic")
    employee_role = forms.CharField(max_length=10, help_text="Enter employee role")
    employee_salary = forms.DecimalField(max_digits=14, decimal_places=4, help_text="Enter employee salary")
    employee_date_of_birth = forms.DateField(help_text="Enter employee date of birth",
                                             widget=forms.DateInput(attrs={'type': 'date'}))
    employee_date_of_start = forms.DateField(help_text="Enter date of employee work started",
                                             widget=forms.DateInput(attrs={'type': 'date'}))
    employee_phone_number = forms.CharField(max_length=13, help_text="Enter employee phone_number")

    def clean_phone_number(self):
        employee_phone_number = self.cleaned_data['phone_number']
        phone_number_pattern = r'^\+?1?\d{9,15}$'
        if not re.match(phone_number_pattern, employee_phone_number):
            raise forms.ValidationError("Please enter a valid phone number.")
        return employee_phone_number

    employee_city = forms.CharField(max_length=50, help_text="Enter employee city")
    employee_street = forms.CharField(max_length=50, help_text="Enter employee street")
    employee_zip_code = forms.CharField(max_length=9, help_text="Enter employee zip code")


class ClientFilterForm(forms.Form):
    client_name = forms.CharField(label='Search', max_length=100, required=False)
    client_discount = forms.IntegerField(help_text="Enter percent of discount", required=False)


class ClientDetailForm(forms.Form):
    card_number = forms.CharField(max_length=13, help_text="Enter employee id")
    cust_surname = forms.CharField(max_length=50, help_text="Enter employee surname")
    cust_name = forms.CharField(max_length=50, help_text="Enter employee name")
    cust_patronymic = forms.CharField(max_length=50, required=False, help_text="Enter patronymic")
    customer_phone_number = forms.CharField(max_length=13, help_text="Enter employee phone_number")

    def clean_phone_number(self):
        employee_phone_number = self.cleaned_data['phone_number']
        phone_number_pattern = r'^\+?1?\d{9,15}$'
        if not re.match(phone_number_pattern, employee_phone_number):
            raise forms.ValidationError("Please enter a valid phone number.")
        return employee_phone_number

    customer_city = forms.CharField(max_length=50, help_text="Enter employee city", required=False)
    customer_street = forms.CharField(max_length=50, help_text="Enter employee street", required=False)
    customer_zip_code = forms.CharField(max_length=9, help_text="Enter employee zip code", required=False)
    customer_discount_percent = forms.IntegerField(help_text="Enter percent of discount", required=False)


class CategoryDetailForm(forms.Form):
    category_name = forms.CharField(label='Category Name', max_length=50)


class UserLoginForm(forms.Form):
    username = forms.CharField(max_length=20, help_text="Enter username")
    password = forms.CharField(max_length=50, help_text="Enter password")

    def clean(self, *args, **kwargs):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if username and password:
            user = authenticate(username=username, password=password)

            if not user:
                raise ValidationError("Incorrect username or password")

            if not user.check_password(password):
                raise ValidationError("Incorrect password")

        return super(UserLoginForm, self).clean()


user = get_user_model()


class UserRegisterForm(forms.Form):
    empl = forms.ChoiceField(choices=None)
    username = forms.CharField(max_length=20, help_text="Enter username")
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = user
        fields = [
            'username',
            'password',
            'empl'
        ]

    def clean(self, *args, **kwargs):
        return super(UserRegisterForm, self).clean()

    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        self.update_choices()

    def update_choices(self):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM store_employee s LEFT JOIN auth_user a ON a.id_employee = s.id_employee WHERE a.id_employee is NULL
            """)
            querys = cursor.fetchall()
        choices = [(row[0], row[1] + " " + row[2]) for row in querys]
        self.fields['empl'].choices = choices
