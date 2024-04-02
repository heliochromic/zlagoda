import re

from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import ValidationError
from django.db import connection

from .models import Category, Employee, Product, Customer_Card


class ProductFilterForm(forms.Form):
    product_name = forms.CharField(label='Search', max_length=100, required=False)
    category_name = forms.ModelChoiceField(queryset=Category.objects.all(), empty_label='All Categories',
                                           required=False)


class ProductDetailForm(forms.Form):
    product_name = forms.CharField(label='Product Name', max_length=100)
    characteristics = forms.CharField(label='Characteristics', widget=forms.Textarea)
    category = forms.ModelChoiceField(queryset=Category.objects.all(), label='Category', empty_label='All Categories')


class EmployeeFilterForm(forms.Form):
    employee_name = forms.CharField(label='Search', max_length=100, required=False)
    empl_role_choices = Employee.objects.values_list('empl_role', flat=True).distinct()
    empl_role_choices = [(role, role) for role in empl_role_choices]
    empl_role_choices.insert(0, ('', 'All Roles'))

    employee_role = forms.ChoiceField(choices=empl_role_choices, required=False)


class EmployeeDetailForm(forms.Form):
    id_employee = forms.CharField(max_length=10, help_text="Enter employee id", required=False)
    employee_name = forms.CharField(max_length=50, help_text="Enter employee name")
    employee_surname = forms.CharField(max_length=50, help_text="Enter employee surname")

    def clean_id_employee(self):
        id_employee = self.cleaned_data['id_employee'] or self.initial['pk']
        print("MGR" in id_employee)
        if "CASH" not in id_employee and "MGR" not in id_employee:
            raise forms.ValidationError("Employee ID has to start with CASH or MGR.")
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM store_employee WHERE id_employee = %s", [id_employee])
            data = cursor.fetchall()
            if len(data) > 0:
                raise forms.ValidationError("This employee ID already exists.")
        return id_employee

    employee_patronymic = forms.CharField(max_length=50, required=False,
                                          help_text="Enter patronymic")
    ROLE_CHOICES = (
        ('manager', 'manager'),
        ('cashier', 'cashier'),
    )
    employee_role = forms.ChoiceField(choices=ROLE_CHOICES, help_text="Enter employee role")
    employee_salary = forms.DecimalField(max_digits=14, decimal_places=4, help_text="Enter employee salary")
    employee_date_of_birth = forms.DateField(help_text="Enter employee date of birth",
                                             widget=forms.DateInput(attrs={'type': 'date'})
                                             )
    employee_date_of_start = forms.DateField(help_text="Enter date of employee work started",
                                             widget=forms.DateInput(attrs={'type': 'date'}))

    def clean(self):
        cleaned_data = super().clean()
        dob = cleaned_data.get('employee_date_of_birth')
        start_date = cleaned_data.get('employee_date_of_start')

        if dob and start_date:
            age = start_date.year - dob.year - ((start_date.month, start_date.day) < (dob.month, dob.day))
            if age < 18:
                raise ValidationError("Employee must be at least 18 years old to start work.")

        return cleaned_data

    employee_phone_number = forms.RegexField(
        regex=r'^\+\d{12}$',
        max_length=13,
        error_messages={
            'regex': "Enter a valid phone number"
        },
        widget=forms.TextInput(attrs={'placeholder': '+123456789012'})
    )
    employee_city = forms.CharField(max_length=50, help_text="Enter employee city")
    employee_street = forms.CharField(max_length=50, help_text="Enter employee street")
    employee_zip_code = forms.CharField(max_length=9, help_text="Enter employee zip code")


class ClientFilterForm(forms.Form):
    client_name = forms.CharField(label='Search', max_length=100, required=False)
    client_discount = forms.IntegerField(help_text="Enter percent of discount", required=False)


class ClientDetailForm(forms.Form):
    card_number = forms.CharField(max_length=13, help_text="Enter employee id", required=False)

    def clean_card_number(self):
        card_number = self.cleaned_data['card_number']
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM store_customer_card WHERE card_number = %s", [card_number])
            data = cursor.fetchall()
            if len(data) > 0:
                raise forms.ValidationError("This card number already exists.")
        return card_number

    cust_surname = forms.CharField(max_length=50, help_text="Enter employee surname")
    cust_name = forms.CharField(max_length=50, help_text="Enter employee name")
    cust_patronymic = forms.CharField(max_length=50, required=False, help_text="Enter patronymic")
    customer_phone_number = forms.RegexField(
        regex=r'^\+\d{12}$',
        max_length=13,
        error_messages={
            'regex': "Enter a valid phone number"
        },
        widget=forms.TextInput(attrs={'placeholder': '+123456789012'})
    )
    customer_city = forms.CharField(max_length=50, help_text="Enter employee city", required=False)
    customer_street = forms.CharField(max_length=50, help_text="Enter employee street", required=False)
    customer_zip_code = forms.CharField(max_length=9, help_text="Enter employee zip code", required=False)
    customer_discount_percent = forms.IntegerField(help_text="Enter percent of discount", required=False)


class CategoryDetailForm(forms.Form):
    category_name = forms.CharField(label='Category Name', max_length=50)

    def clean(self):
        category_name = self.cleaned_data.get('category_name')
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM store_category WHERE category_name = %s", [category_name])
            data = cursor.fetchall()
            if len(data) > 0 and data[0][0] != self.initial['pk']:
                raise forms.ValidationError("This category name already exists.")
        return category_name


class CheckDetailForm(forms.Form):
    card_number = forms.ModelChoiceField(queryset=Customer_Card.objects.all(), required=False,
                                         help_text="Enter card number associated with receipt")


class CheckProductDetailForm(forms.Form):
    product_upc = forms.CharField(label="Product UPC", max_length=12)
    quantity = forms.IntegerField(label="Quantity")

    def check_product_stock(self):
        product_upc = self.cleaned_data.get('product_upc')
        quantity = self.cleaned_data.get('quantity')

        query = """
        SELECT products_number FROM store_store_product WHERE "UPC" == %s;
        """

        with connection.cursor() as cursor:
            cursor.execute(query, [product_upc])
            store_quantity = cursor.fetchall()[0]

        if quantity > store_quantity:
            raise forms.ValidationError(f"Insufficient stock for product with UPC {product_upc}")


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
