import decimal
import json
import random
from datetime import date, datetime

from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.sessions.models import Session
from django.utils.decorators import method_decorator
from django.db import connection, transaction, IntegrityError
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, reverse, redirect, HttpResponseRedirect
from django.views import View
from django.contrib import messages
from django.urls import reverse_lazy

from .forms import (ProductFilterForm, ProductDetailForm, EmployeeFilterForm, EmployeeDetailForm, \
                    ClientFilterForm, ClientDetailForm, CategoryDetailForm, UserLoginForm, UserRegisterForm,
                    StoreProductFilterForm, \
                    StoreProductDetailForm, StorePromotionalProductDetailForm, CustomPasswordChangeForm)

from .forms import ProductFilterForm, ProductDetailForm, EmployeeFilterForm, EmployeeDetailForm, \
    ClientFilterForm, ClientDetailForm, CategoryDetailForm, UserLoginForm, UserRegisterForm, CheckProductDetailForm, \
    CheckDetailForm, CheckFilter, StatsDateOptions


# Create your views here


def index(request):
    return redirect('product-list')


@method_decorator(login_required, name='dispatch')
class EmployeeListView(View):
    template_name = 'store/employee/employee-list.html'

    def get(self, request):
        form = EmployeeFilterForm(request.GET)

        query = '''
                    SELECT id_employee, CONCAT(empl_surname, ' ',empl_name) AS full_name, empl_role, phone_number, 
                    CONCAT(street, ', ', city, ' ', zip_code) as address
                    FROM store_employee 
                '''

        if form.is_valid():
            empl_name = form.cleaned_data.get('employee_name')
            selected_role = form.cleaned_data.get('employee_role')

            query_params = []

            if selected_role:
                query += 'WHERE empl_role = %s '
                query_params.append(selected_role)

            if empl_name:
                if selected_role:
                    query += 'AND CONCAT(empl_surname, \' \', empl_name) ILIKE %s'
                else:
                    query += 'WHERE CONCAT(empl_surname, \' \', empl_name) ILIKE %s'
                query_params.append(f'%{empl_name}%')

            with connection.cursor() as cursor:
                query += 'ORDER BY 2'
                cursor.execute(query, query_params)
                employees = cursor.fetchall()

        else:
            with connection.cursor() as cursor:
                query += 'ORDER BY 2'
                cursor.execute(query)
                employees = cursor.fetchall()

        return render(request, template_name=self.template_name, context={
            'form': form,
            'employees': employees
        })


@method_decorator(login_required, name='dispatch')
class EmployeeCreateView(View):
    template_name = 'store/employee/employee-add.html'
    success_url = reverse_lazy('employee-list')

    def get(self, request):
        return render(request, template_name=self.template_name, context={
            'form': EmployeeDetailForm()
        })

    def post(self, request):
        form = EmployeeDetailForm(request.POST)
        if form.is_valid():
            params = []
            selected_id = form.cleaned_data.get("id_employee")
            params.append(selected_id)
            selected_surname = form.cleaned_data.get('employee_surname')
            params.append(selected_surname)
            selected_name = form.cleaned_data.get('employee_name')
            params.append(selected_name)
            selected_patronymic = form.cleaned_data.get('employee_patronymic')
            params.append(selected_patronymic)
            selected_role = 'Cashier' if 'CASH' in selected_id else 'Manager'
            params.append(selected_role)
            selected_salary = form.cleaned_data.get('employee_salary')
            params.append(selected_salary)
            selected_date_of_birth = form.cleaned_data.get('employee_date_of_birth')
            params.append(selected_date_of_birth)
            selected_date_of_start = form.cleaned_data.get('employee_date_of_start')
            params.append(selected_date_of_start)
            selected_phone_number = form.cleaned_data.get('employee_phone_number')
            params.append(selected_phone_number)
            selected_city = form.cleaned_data.get('employee_city')
            params.append(selected_city)
            selected_street = form.cleaned_data.get('employee_street')
            params.append(selected_street)
            selected_zipcode = form.cleaned_data.get('employee_zip_code')
            params.append(selected_zipcode)
            insert = """
                   INSERT INTO store_employee VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
               """
            with connection.cursor() as cursor:
                cursor.execute(insert,
                               params)

            messages.success(request, 'Product added successfully')
            return redirect(self.success_url)
        else:
            return render(request, template_name=self.template_name, context={
                'form': form
            })


@method_decorator(login_required, name='dispatch')
class EmployeeDetailView(View):
    template_name = 'store/employee/employee-detail.html'
    success_url = reverse_lazy('employee-list')

    def get(self, request, pk):
        query = '''
            SELECT * FROM store_employee WHERE id_employee = %s
            '''
        with connection.cursor() as cursor:
            cursor.execute(query, [pk])
            employee = cursor.fetchall()

        (id_employee, employee_surname
         , employee_name, employee_patronymic, employee_role
         , employee_salary, employee_date_of_birth
         , employee_date_of_start, employee_phone_number
         , employee_city, employee_street, employee_zip_code) = (employee[0][0], employee[0][1]
                                                                 , employee[0][2], employee[0][3], employee[0][4]
                                                                 , employee[0][5], employee[0][6]
                                                                 , employee[0][7], employee[0][8], employee[0][9]
                                                                 , employee[0][10], employee[0][11])

        form = EmployeeDetailForm(initial={
            'id_employee': id_employee,
            'employee_surname': employee_surname,
            'employee_name': employee_name,
            'employee_patronymic': employee_patronymic,
            'employee_role': employee_role,
            'employee_salary': employee_salary,
            'employee_date_of_birth': employee_date_of_birth,
            'employee_date_of_start': employee_date_of_start,
            'employee_phone_number': employee_phone_number,
            'employee_city': employee_city,
            'employee_street': employee_street,
            'employee_zip_code': employee_zip_code
        })

        return render(request, template_name=self.template_name, context={
            'form': form,
            'pk': pk,
            'role': employee_role
        })

    def post(self, request, pk):
        if request.POST.get('action') == 'delete':
            return self.delete_employee(request, pk)
        else:
            return self.update_employee(request, pk)

    def delete_employee(self, request, pk):
        try:

            delete_employee_group = 'DELETE FROM auth_user_groups WHERE user_id = %s'
            delete_employee = 'DELETE FROM auth_user WHERE id_employee = %s'
            delete = 'DELETE FROM store_employee WHERE id_employee = %s'

            with connection.cursor() as cursor:
                with transaction.atomic():
                    cursor.execute('SELECT id FROM auth_user WHERE id_employee=%s', [pk])
                    user_id = cursor.fetchone()[0]
                    cursor.execute(delete_employee_group, [user_id])
                    cursor.execute(delete_employee, [pk])
                    cursor.execute(delete, [pk])

            messages.success(request, 'Employee deleted successfully')
            return redirect(self.success_url)
        except IntegrityError as e:
            print(e)
            return HttpResponseRedirect('{}?submit=No'.format(request.path))

    def update_employee(self, request, pk):
        with connection.cursor() as cursor:
            cursor.execute("SELECT empl_role FROM store_employee WHERE id_employee =%s", [pk])
            role = cursor.fetchone()[0]
        form = EmployeeDetailForm(request.POST, initial={'pk': pk, 'role': role})
        if form.is_valid():
            params = []
            selected_id = pk
            params.append(selected_id)
            selected_surname = form.cleaned_data.get('employee_surname')
            params.append(selected_surname)
            selected_name = form.cleaned_data.get('employee_name')
            params.append(selected_name)
            selected_patronymic = form.cleaned_data.get('employee_patronymic')
            params.append(selected_patronymic)
            selected_role = role
            params.append(selected_role)
            selected_salary = form.cleaned_data.get('employee_salary')
            params.append(selected_salary)
            selected_date_of_birth = form.cleaned_data.get('employee_date_of_birth')
            params.append(selected_date_of_birth)
            selected_date_of_start = form.cleaned_data.get('employee_date_of_start')
            params.append(selected_date_of_start)
            selected_phone_number = form.cleaned_data.get('employee_phone_number')
            params.append(selected_phone_number)
            selected_city = form.cleaned_data.get('employee_city')
            params.append(selected_city)
            selected_street = form.cleaned_data.get('employee_street')
            params.append(selected_street)
            selected_zipcode = form.cleaned_data.get('employee_zip_code')
            params.append(selected_zipcode)
            params.append(pk)

            update = '''
                UPDATE store_employee
                SET id_employee = %s, empl_surname = %s, empl_name = %s,
                    empl_patronymic = %s,empl_role = %s, salary = %s,
                    date_of_birth = %s, date_of_start = %s, phone_number = %s,
                    city = %s, street = %s, zip_code = %s
                WHERE id_employee = %s
                '''

            with connection.cursor() as cursor:
                cursor.execute(update, params)

            messages.success(request, 'Employee updated successfully')
            return redirect(self.success_url)
        else:
            return render(request, template_name=self.template_name, context={
                'form': form,
                'pk': pk,
                'role': role
            })


@method_decorator(login_required, name='dispatch')
class ClientListView(View):
    template_name = 'store/client/client-list.html'

    def get(self, request):
        form = ClientFilterForm(request.GET)

        query = '''
                        SELECT card_number, CONCAT(cust_surname, ' ',cust_name) AS full_name, phone_number, 
                        CONCAT(street, ', ', city, ' ', zip_code) as address, percent as discount
                        FROM store_customer_card
                    '''
        if form.is_valid():
            cust_name = form.cleaned_data.get('client_name')
            discount = form.cleaned_data.get('client_discount')

            query_params = []

            if discount:
                query += 'WHERE percent = %s '
                query_params.append(discount)

            if cust_name:
                if discount:
                    query += 'AND CONCAT(cust_surname, \' \', cust_name) ILIKE %s'
                else:
                    query += 'WHERE CONCAT(cust_surname, \' \', cust_name) ILIKE %s'
                query_params.append(f'%{cust_name}%')

            with connection.cursor() as cursor:
                query += 'ORDER BY 2'
                cursor.execute(query, query_params)
                clients = cursor.fetchall()

        else:
            with connection.cursor() as cursor:
                query += 'ORDER BY 2'
                cursor.execute(query)
                clients = cursor.fetchall()

        return render(request, template_name=self.template_name, context={
            'form': form,
            'clients': clients,

        })


@method_decorator(login_required, name='dispatch')
class ClientCreateView(View):
    template_name = 'store/client/client-add.html'
    success_url = reverse_lazy('client-list')  # Assuming 'product_list' is the name of your product list URL

    def get(self, request):
        return render(request, template_name=self.template_name, context={
            'form': ClientDetailForm()
        })

    def post(self, request):
        form = ClientDetailForm(request.POST)
        if form.is_valid():
            params = []
            selected_id = form.cleaned_data.get("card_number")
            params.append(selected_id)
            selected_surname = form.cleaned_data.get('cust_surname')
            params.append(selected_surname)
            selected_name = form.cleaned_data.get('cust_name')
            params.append(selected_name)
            selected_patronymic = form.cleaned_data.get('cust_patronymic')
            params.append(selected_patronymic)
            selected_phone_number = form.cleaned_data.get('customer_phone_number')
            params.append(selected_phone_number)
            selected_city = form.cleaned_data.get('customer_city')
            params.append(selected_city)
            selected_street = form.cleaned_data.get('customer_street')
            params.append(selected_street)
            selected_zipcode = form.cleaned_data.get('customer_zip_code')
            params.append(selected_zipcode)
            selected_percent = form.cleaned_data.get('customer_discount_percent')
            params.append(selected_percent)
            insert = """
                       INSERT INTO store_customer_card VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
                   """
            with connection.cursor() as cursor:
                cursor.execute(insert, params)

            messages.success(request, 'Product added successfully')
            return redirect(self.success_url)
        else:
            return render(request, template_name=self.template_name, context={
                'form': form
            })


@method_decorator(login_required, name='dispatch')
class ClientUpdateView(View):
    template_name = 'store/client/client-detail.html'
    success_url = reverse_lazy('client-list')

    def get(self, request, pk):
        query = '''
               SELECT * FROM store_customer_card WHERE card_number = %s
               '''
        with connection.cursor() as cursor:
            cursor.execute(query, [pk])
            client = cursor.fetchall()

        (card_number, cust_name
         , cust_surname, cust_patronymic, customer_phone_number
         , customer_city, customer_street
         , customer_zip_code, customer_discount_percent) = (client[0][0], client[0][1]
                                                            , client[0][2], client[0][3], client[0][4]
                                                            , client[0][5], client[0][6]
                                                            , client[0][7], client[0][8])

        form = ClientDetailForm(initial={
            'card_number': card_number,
            'cust_name': cust_name,
            'cust_surname': cust_surname,
            'cust_patronymic': cust_patronymic,
            'customer_phone_number': customer_phone_number,
            'customer_city': customer_city,
            'customer_street': customer_street,
            'customer_zip_code': customer_zip_code,
            'customer_discount_percent': customer_discount_percent
        })

        return render(request, template_name=self.template_name, context={
            'form': form,
            'pk': pk,
        })

    def post(self, request, pk):
        if request.POST.get('action') == 'delete':
            return self.delete_client(request, pk)
        else:
            return self.update_client(request, pk)

    def delete_client(self, request, pk):
        try:
            delete = 'DELETE FROM store_customer_card WHERE card_number = %s'

            with connection.cursor() as cursor:
                cursor.execute(delete, [pk])

            messages.success(request, 'Employee deleted successfully')
            return redirect(self.success_url)
        except IntegrityError:
            return HttpResponseRedirect('{}?submit=No'.format(request.path))

    def update_client(self, request, pk):
        form = ClientDetailForm(request.POST)
        if form.is_valid():
            params = []
            selected_id = pk
            params.append(selected_id)
            selected_surname = form.cleaned_data.get('cust_surname')
            params.append(selected_surname)
            selected_name = form.cleaned_data.get('cust_name')
            params.append(selected_name)
            selected_patronymic = form.cleaned_data.get('cust_patronymic')
            params.append(selected_patronymic)
            selected_phone_number = form.cleaned_data.get('customer_phone_number')
            params.append(selected_phone_number)
            selected_city = form.cleaned_data.get('customer_city')
            params.append(selected_city)
            selected_street = form.cleaned_data.get('customer_street')
            params.append(selected_street)
            selected_zipcode = form.cleaned_data.get('customer_zip_code')
            params.append(selected_zipcode)
            selected_percent = form.cleaned_data.get('customer_discount_percent')
            params.append(selected_percent)
            params.append(pk)

            update = '''
                   UPDATE store_customer_card
                   SET card_number = %s, cust_surname = %s, cust_name = %s,
                       cust_patronymic = %s, phone_number = %s, city = %s,
                       street = %s, zip_code = %s, percent = %s
                   WHERE card_number = %s
                   '''

            with connection.cursor() as cursor:
                cursor.execute(update, params)

            messages.success(request, 'Client updated successfully')
            return redirect(self.success_url)
        else:
            return render(request, template_name=self.template_name, context={
                'form': form,
                'pk': pk
            })


@method_decorator(login_required, name='dispatch')
class CategoryListView(View):
    template_name = 'store/category/category-list.html'

    def get(self, request):
        query = '''
                SELECT category_number, category_name
                FROM store_category AS p
                '''

        with connection.cursor() as cursor:
            query += 'ORDER BY 2'
            cursor.execute(query)
            categories = cursor.fetchall()

        return render(request, template_name=self.template_name, context={
            'categories': categories
        })


@method_decorator(login_required, name='dispatch')
class CategoryCreateView(View):
    template_name = 'store/category/category-add.html'
    success_url = reverse_lazy('category-list')

    def get(self, request):
        return render(request, template_name=self.template_name, context={
            'form': CategoryDetailForm()
        })

    def post(self, request):
        form = CategoryDetailForm(request.POST, initial={'pk': 0})
        if form.is_valid():
            selected_name = form.cleaned_data
            insert = """
                   INSERT INTO store_category (category_name) VALUES (%s);
               """

            with connection.cursor() as cursor:
                cursor.execute(insert, [selected_name])

            messages.success(request, 'Category added successfully')
            return redirect(self.success_url)
        else:
            return render(request, template_name=self.template_name, context={
                'form': form
            })


@method_decorator(login_required, name='dispatch')
class CategoryUpdateView(View):
    template_name = 'store/category/category-detail.html'
    success_url = reverse_lazy('category-list')

    def get(self, request, pk):
        query = '''
                SELECT * FROM store_category WHERE category_number = %s
                '''
        with connection.cursor() as cursor:
            cursor.execute(query, [pk])
            category = cursor.fetchall()

        category_name = category[0][1]

        form = CategoryDetailForm(initial={
            'category_name': category_name
        })

        return render(request, template_name=self.template_name, context={
            'form': form,
            'pk': pk,
        })

    def post(self, request, pk):
        if request.POST.get('action') == 'delete':
            return self.delete_category(request, pk)
        else:
            return self.update_category(request, pk)

    def delete_category(self, request, pk):
        try:
            delete = 'DELETE FROM store_category WHERE category_number = %s'

            with connection.cursor() as cursor:
                cursor.execute(delete, [pk])

            messages.success(request, 'Category deleted successfully')
            return redirect(self.success_url)
        except IntegrityError:
            return HttpResponseRedirect('{}?submit=No'.format(request.path))

    def update_category(self, request, pk):
        form = CategoryDetailForm(request.POST, initial={"pk": pk})
        if form.is_valid():
            selected_category = form.cleaned_data
            update = '''
                    UPDATE store_category 
                    SET category_name = %s
                    WHERE category_number = %s
                    '''

            with connection.cursor() as cursor:
                cursor.execute(update,
                               [selected_category, pk])

            messages.success(request, 'Category updated successfully')
            return redirect(self.success_url)
        else:
            return render(request, template_name=self.template_name, context={
                'form': form,
                'pk': pk
            })


@method_decorator(login_required, name='dispatch')
class ProductListView(View):
    template_name = 'store/product/product-list.html'

    def get(self, request):
        form = ProductFilterForm(request.GET)

        query = '''
            SELECT p.id_product, p.product_name, p.characteristics, c.category_name
            FROM store_product AS p
            INNER JOIN store_category AS c ON p.category_number_id = c.category_number
            '''

        if form.is_valid():
            product_name = form.cleaned_data.get('product_name')
            selected_category = form.cleaned_data.get('category_name')

            query_params = []

            if selected_category:
                query += 'WHERE c.category_name = %s '
                query_params.append(selected_category.category_name)

            if product_name:
                if selected_category:
                    query += 'AND p.product_name ILIKE %s'
                else:
                    query += 'WHERE p.product_name ILIKE %s'
                query_params.append(f'%{product_name}%')

            with connection.cursor() as cursor:
                query += 'ORDER BY 2'
                cursor.execute(query, query_params)
                products = cursor.fetchall()

        else:
            with connection.cursor() as cursor:
                query += 'ORDER BY 2'
                cursor.execute(query)
                products = cursor.fetchall()

        return render(request, template_name=self.template_name, context={
            'form': form,
            'products': products
        })


@method_decorator(login_required, name='dispatch')
class ProductCreateView(View):
    template_name = 'store/product/product-add.html'
    success_url = reverse_lazy('product-list')

    def get(self, request):
        return render(request, template_name=self.template_name, context={
            'form': ProductDetailForm()
        })

    def post(self, request):
        form = ProductDetailForm(request.POST)
        if form.is_valid():
            selected_category = form.cleaned_data.get('category')
            selected_product_name = form.cleaned_data.get('product_name')
            selected_characteristics = form.cleaned_data.get('characteristics')

            insert = """
                INSERT INTO store_product (product_name, characteristics, category_number_id) VALUES (%s, %s, %s);
            """

            with connection.cursor() as cursor:
                cursor.execute(insert,
                               [selected_product_name, selected_characteristics, selected_category.category_number])

            messages.success(request, 'Product added successfully')
            return redirect(self.success_url)
        else:
            return render(request, template_name=self.template_name, context={
                'form': form
            })


@method_decorator(login_required, name='dispatch')
class ProductDetailView(View):
    template_name = 'store/product/product-detail.html'
    success_url = reverse_lazy('product-list')

    def get(self, request, pk):
        query = '''
            SELECT * FROM store_product WHERE id_product = %s
            '''
        with connection.cursor() as cursor:
            cursor.execute(query, [pk])
            product = cursor.fetchall()

        product_name, characteristics, category = product[0][1], product[0][2], product[0][3]

        form = ProductDetailForm(initial={
            'product_name': product_name,
            'characteristics': characteristics,
            'category': category
        })

        return render(request, template_name=self.template_name, context={
            'form': form,
            'pk': pk,
        })

    def post(self, request, pk):
        if 'action' in request.POST:
            if request.POST.get('action') == 'delete':
                return self.delete_product(request, pk)
            elif 'start_date' in request.POST and 'end_date' in request.POST:
                print("get count action")
                return self.get_sales_count_form(request, pk)
        else:
            print("get update action")
            return self.update_product(request, pk)

    def delete_product(self, request, pk):
        try:
            delete = 'DELETE FROM store_product WHERE id_product = %s'
            with connection.cursor() as cursor:
                cursor.execute(delete, [pk])

            messages.success(request, 'Store product deleted successfully')
            return redirect(self.success_url)
        except IntegrityError:
            return HttpResponseRedirect('{}?submit=No'.format(request.path))

    def update_product(self, request, pk):
        form = ProductDetailForm(request.POST)

        if form.is_valid():
            selected_category = form.cleaned_data.get('category')
            selected_product_name = form.cleaned_data.get('product_name')
            selected_characteristics = form.cleaned_data.get('characteristics')

            update = '''
                UPDATE store_product 
                SET product_name = %s, characteristics = %s, category_number_id = %s
                WHERE id_product = %s
                '''

            with connection.cursor() as cursor:
                cursor.execute(update,
                               [selected_product_name, selected_characteristics, selected_category.category_number, pk])

            messages.success(request, 'Product added successfully')
            return redirect(self.success_url)
        else:
            return render(request, template_name=self.template_name, context={
                'form': form,
                'pk': pk
            })

    def get_sales_count(self, start_date, end_date, product_id):
        query = '''
            SELECT SUM(sa.product_number) 
            FROM store_product s JOIN store_store_product ss
            ON s.id_product = ss.id_product_id JOIN store_sale sa 
            ON sa."UPC_id" = ss."UPC" JOIN store_check c 
            ON c.check_number = sa.check_number_id
            WHERE s.id_product = %s AND c.print_date BETWEEN %s AND %s
        '''
        with connection.cursor() as cursor:
            cursor.execute(query, [product_id, start_date, end_date])
            sales_count = cursor.fetchone()[0]
        return sales_count

    def get_sales_count_form(self, request, pk):
        query = '''
                   SELECT * FROM store_product WHERE id_product = %s
                   '''
        with connection.cursor() as cursor:
            cursor.execute(query, [pk])
            product = cursor.fetchall()

        product_name, characteristics, category = product[0][1], product[0][2], product[0][3]
        if request.method == 'POST':
            start_date = request.POST.get('start_date') or '2000-01-01'
            end_date = request.POST.get('end_date') or '9999-12-31'
            sales_count = self.get_sales_count(start_date, end_date, pk)
            form = ProductDetailForm(initial={
                'product_name': product_name,
                'characteristics': characteristics,
                'category': category,
                'start_date': start_date,
                'end_date': end_date,
            })
            return render(request, template_name=self.template_name, context={
                'form': form,
                'pk': pk,
                'sales_count': sales_count,
                'start_date': start_date,
                'end_date': end_date,
            })
        form = ProductDetailForm(initial={
            'product_name': product_name,
            'characteristics': characteristics,
            'category': category
        })
        return render(request, template_name=self.template_name, context={
            'form': form,
            'pk': pk,
        })


@method_decorator(login_required, name='dispatch')
class StoreProductListView(View):
    template_name = 'store/store-product/store-product-list.html'
    success_url = reverse_lazy('store-product-list')

    def get(self, request):
        form = StoreProductFilterForm(request.GET)

        query = """
                    SELECT ssp."UPC", sp.product_name, sp.characteristics,
                           ssp.selling_price, ssp.products_number, 
                           ssp.promotional_product
                    FROM store_store_product AS ssp
                    INNER JOIN store_product AS sp
                    ON ssp.id_product_id = sp.id_product
                    """

        if form.is_valid():
            selected_upc = form.cleaned_data.get('product_upc')
            show_sales = form.cleaned_data.get('discount_available')
            show_full_price = form.cleaned_data.get('discount_unavailable')
            sort_by_name = form.cleaned_data.get('sort_by_name')
            sort_by_quantity = form.cleaned_data.get('sort_by_quantity')

            query_params = []
            if selected_upc:
                query += 'WHERE ssp."UPC" ILIKE %s '
                query_params.append(f'%{selected_upc}%')
            if show_sales:
                if selected_upc:
                    if show_full_price:
                        query += 'AND (ssp.promotional_product = true OR ssp.promotional_product = false)'
                    else:
                        query += 'AND ssp.promotional_product = true'
                else:
                    query += 'WHERE ssp.promotional_product=true'
                    query_params.append(show_sales)
            if show_full_price:
                if show_sales and not selected_upc:
                    query += ' OR ssp.promotional_product = false'
                elif selected_upc and not show_sales:
                    query += 'AND ssp.promotional_product = false'
                elif not show_sales and not selected_upc:
                    query += ' WHERE ssp.promotional_product = false'

            with connection.cursor() as cursor:
                if sort_by_name:
                    query += ' ORDER BY sp.product_name'
                if sort_by_quantity:
                    if sort_by_name:
                        query += ', ssp.products_number DESC'
                    else:
                        query += ' ORDER BY ssp.products_number DESC'
                cursor.execute(query, query_params)
                store_products = cursor.fetchall()
        else:
            with connection.cursor() as cursor:
                query += ' ORDER BY sp.product_name'
                cursor.execute(query)
                store_products = cursor.fetchall()

        return render(request, template_name=self.template_name, context={
            'form': form,
            'store_products': store_products
        })

    def post(self, request):
        pk = request.POST.get('product_id')
        if request.POST.get('action') == 'delete':
            return self.delete_promotional_store_product(request, pk)
        else:
            return self.add_promotional_product(request, pk)

    def add_promotional_product(self, request, pk):
        selected_product_query = '''
                                        SELECT * FROM store_store_product WHERE "UPC" = %s
                                 '''

        with connection.cursor() as cursor:
            cursor.execute(selected_product_query, [pk])
            main_product = cursor.fetchall()
        if not main_product[0][4]:
            product_upc = ''.join(random.choices('0123456789', k=12))
            while not StoreProductListView.check_correct_upc(product_upc):
                product_upc = ''.join(random.choices('0123456789', k=12))
                print(f"created UPC {product_upc}")
            print(f"created UPC{product_upc}")
            id_product = main_product[0][5]
            selling_price = main_product[0][1] * decimal.Decimal('0.8')
            product_number = main_product[0][2]
            promotional_product = True
            upc_prom = None

            query_params = (product_upc, selling_price, product_number, promotional_product,
                            upc_prom, id_product)

            insert = """
                                       INSERT INTO store_store_product ("UPC", selling_price, products_number, 
                                                                        promotional_product,"UPC_prom_id", 
                                                                        id_product_id) 
                                                                        VALUES (%s, %s, %s, %s, %s, %s);
                                       """
            renewal_store_product = '''
                                                      UPDATE store_store_product
                                                      SET "UPC_prom_id" = %s, products_number = 0
                                                      WHERE "UPC" = %s
                                          '''
            with connection.cursor() as cursor:
                cursor.execute(insert, query_params)
                cursor.execute(renewal_store_product, [product_upc, pk])
        else:
            update_promotional = '''
                                    UPDATE store_store_product
                                    SET "products_number" = "products_number" + %s
                                    WHERE "UPC" = %s
                                          '''
            update_main_product = '''
                                    UPDATE store_store_product
                                    SET "products_number" = 0
                                    WHERE "UPC" = %s
                                          '''
            with connection.cursor() as cursor:
                cursor.execute(update_promotional, [main_product[0][2], main_product[0][4]])
                cursor.execute(update_main_product, [main_product[0][0]])

        messages.success(request, 'Promotional Store Product added successfully')
        return redirect(self.success_url)

    def delete_promotional_store_product(self, request, pk):
        try:
            delete = '''UPDATE store_store_product
                        SET products_number = 0
                        WHERE "UPC" = %s '''

            with connection.cursor() as cursor:
                cursor.execute(delete, [pk])

            messages.success(request, 'Promotional Store product deleted successfully')
            return redirect(self.success_url)
        except IntegrityError:
            return HttpResponseRedirect('{}?submit=No'.format(request.path))

    @staticmethod
    def check_correct_upc(entered_upc: str) -> bool:
        query = '''
                                        SELECT * FROM store_store_product WHERE "UPC" = %s
                                 '''
        with connection.cursor() as cursor:
            cursor.execute(query, [entered_upc])
            existing_product = cursor.fetchall()
        if existing_product:
            return False
        else:
            return True


@method_decorator(login_required, name='dispatch')
class StoreProductCreateView(View):
    template_name = 'store/store-product/store-product-add.html'
    success_url = reverse_lazy('store-product-list')

    def get(self, request):
        return render(request, template_name=self.template_name, context={
            'form': StoreProductDetailForm()
        })

    def post(self, request):
        form = StoreProductDetailForm(request.POST)
        if form.is_valid():
            product_upc = form.cleaned_data.get('product_upc')
            id_product = form.cleaned_data.get('id_product_id')
            selling_price = form.cleaned_data.get('selling_price')
            product_number = form.cleaned_data.get('products_number')
            promotional_product = False
            upc_prom = None

            query_params = (product_upc, selling_price, product_number, promotional_product,
                            upc_prom, id_product.id_product)

            check_exist_query = '''
                        SELECT * FROM store_store_product WHERE id_product_id = %s AND promotional_product = false;
            '''
            with connection.cursor() as cursor:
                cursor.execute(check_exist_query, [id_product.id_product])
                store_product = cursor.fetchall()

            if store_product:
                new_product_num = store_product[0][2] + product_number
                new_selling_price = selling_price
                promotional_selling_price = selling_price * decimal.Decimal('0.8')
                renewal_store_product = '''
                            UPDATE store_store_product
                            SET selling_price = %s, products_number = %s
                            WHERE "UPC" = %s  
                '''
                update_promotional = '''UPDATE store_store_product
                                        SET selling_price = %s
                                        WHERE "UPC" = %s 
                                        '''
                with connection.cursor() as cursor:
                    cursor.execute(renewal_store_product,
                                   [new_selling_price, new_product_num, store_product[0][0]])
                    if store_product[0][4]:
                        cursor.execute(update_promotional, [promotional_selling_price, store_product[0][4]])
            else:
                insert = """
                        INSERT INTO store_store_product ("UPC", selling_price, products_number, promotional_product, 
                                                        "UPC_prom_id", id_product_id) VALUES (%s, %s, %s, %s, %s, %s);
                              """
                try:
                    with connection.cursor() as cursor:
                        cursor.execute(insert, query_params)
                except IntegrityError:
                    return HttpResponseRedirect('{}?submit=No'.format(request.path))

            messages.success(request, 'Store Product added successfully')
            return redirect(self.success_url)
        else:
            return render(request, template_name=self.template_name, context={
                'form': form
            })


@method_decorator(login_required, name='dispatch')
class StoreProductUpdateView(View):
    template_name = 'store/store-product/store-product-detail.html'
    success_url = reverse_lazy('store-product-list')

    def get(self, request, pk):
        query = '''
                 SELECT * FROM store_store_product WHERE "UPC" = %s 
                 '''
        with connection.cursor() as cursor:
            cursor.execute(query, [pk])
            store_product = cursor.fetchall()

        upc_prod, selling_price, prod_number, promotional_product, upc_prom_id, id_prod = (store_product[0][0],
                                                                                           store_product[0][1],
                                                                                           store_product[0][2],
                                                                                           store_product[0][3],
                                                                                           store_product[0][4],
                                                                                           store_product[0][5])

        query_connected_product = '''
                    SELECT * FROM store_product WHERE id_product = %s
        '''

        with connection.cursor() as cursor:
            cursor.execute(query_connected_product, [id_prod])
            connected_product = cursor.fetchall()

        prod_name, prod_characteristics = connected_product[0][1], connected_product[0][2]
        form = StoreProductDetailForm(initial={
            'product_upc': upc_prod,
            'selling_price': selling_price,
            'products_number': prod_number,
            'id_product_id': id_prod
        })
        form1 = StorePromotionalProductDetailForm(initial={
            'products_number': prod_number
        })
        return render(request, template_name=self.template_name, context={
            'form': form1 if promotional_product else form,
            'pk': pk,
            'upc_promotional': upc_prom_id,
            'selling_price': selling_price,
            'promotional_product': promotional_product,
            'upc_prod': upc_prod,
            'prod_name': prod_name,
            'prod_characteristics': prod_characteristics
        })

    def post(self, request, pk):
        query = '''
                         SELECT * FROM store_store_product WHERE "UPC" = %s 
                         '''
        with connection.cursor() as cursor:
            cursor.execute(query, [pk])
            store_product = cursor.fetchall()

        if request.POST.get('action') == 'delete':
            if store_product[0][3]:
                return self.delete_promotional_store_product(request, pk)
            else:
                return self.delete_store_product(request, pk)
        else:
            if store_product[0][3]:
                return self.update_promotional_store_product(request, pk)
            else:
                return self.update_store_product(request, pk)

    def delete_store_product(self, request, pk):
        try:
            query_selected = ''' SELECT * FROM store_store_product WHERE "UPC" = %s
            '''
            with connection.cursor() as cursor:
                cursor.execute(query_selected, [pk])
                selected_product = cursor.fetchall()

            select_from_sale = ''' SELECT * 
                                  FROM store_sale WHERE "UPC_id" = %s'''
            with connection.cursor() as cursor:
                cursor.execute(select_from_sale, [selected_product[0][4]])
                sale_product = cursor.fetchone()

            if sale_product:
                return HttpResponseRedirect('{}?submit=No'.format(request.path))

            delete = 'DELETE FROM store_store_product WHERE "UPC" = %s '

            with connection.cursor() as cursor:
                cursor.execute(delete, [pk])
                if selected_product[0][4]:
                    cursor.execute('DELETE FROM store_store_product WHERE "UPC" = %s', [selected_product[0][4]])

            messages.success(request, 'Store product deleted successfully')
            return redirect(self.success_url)
        except IntegrityError:
            return HttpResponseRedirect('{}?submit=No'.format(request.path))

    def delete_promotional_store_product(self, request, pk):
        try:
            delete = '''UPDATE store_store_product
                        SET products_number = 0
                        WHERE "UPC" = %s '''

            with connection.cursor() as cursor:
                cursor.execute(delete, [pk])

            messages.success(request, 'Store product deleted successfully')
            return redirect(self.success_url)
        except IntegrityError:
            return HttpResponseRedirect('{}?submit=No'.format(request.path))

    def update_store_product(self, request, pk):
        form = StoreProductDetailForm(request.POST)

        if form.is_valid():
            selected_selling_price = form.cleaned_data.get('selling_price')
            selected_prod_number = form.cleaned_data.get('products_number')
            print('VALIDDDD')
            promotional_selling_price = selected_selling_price * decimal.Decimal('0.8')
            query_selected = ''' SELECT * FROM store_store_product WHERE "UPC" = %s
                        '''
            with connection.cursor() as cursor:
                cursor.execute(query_selected, [pk])
                selected_product = cursor.fetchall()

            update = '''UPDATE store_store_product
                        SET selling_price = %s, products_number = %s
                        WHERE "UPC" = %s
                        '''

            update_promotional = '''UPDATE store_store_product
                        SET selling_price = %s
                        WHERE "UPC" = %s 
                        '''

            with connection.cursor() as cursor:
                cursor.execute(update,
                               [selected_selling_price, selected_prod_number, pk])
                if selected_product[0][4]:
                    cursor.execute(update_promotional, [promotional_selling_price, selected_product[0][4]])

            messages.success(request, 'Store Product added successfully')
            return redirect(self.success_url)
        else:
            selected_product = '''
                        SELECT * FROM store_store_product WHERE "UPC" = %s
                 '''

            print('ya invalid')
            with connection.cursor() as cursor:
                cursor.execute(selected_product, [pk])
                selected_prod = cursor.fetchall()

            product = '''
                        SELECT * FROM store_product WHERE "id_product" = %s
                 '''
            with connection.cursor() as cursor:
                cursor.execute(product, [selected_prod[0][5]])
                prod = cursor.fetchall()
            prod_name, prod_characteristics = prod[0][1], prod[0][2]

            return render(request, template_name=self.template_name, context={
                'form': form,
                'pk': pk,
                'upc_prod': pk,
                'prod_name': prod_name,
                'prod_characteristics': prod_characteristics,
            })

    def update_promotional_store_product(self, request, pk):
        form = StorePromotionalProductDetailForm(request.POST)

        if form.is_valid():
            selected_prod_number = form.cleaned_data.get('products_number')
            print('VALIDDDD')

            update = '''UPDATE store_store_product
                           SET products_number = %s
                           WHERE "UPC" = %s
                           '''

            with connection.cursor() as cursor:
                cursor.execute(update,
                               [selected_prod_number, pk])

            messages.success(request, 'Store Product added successfully')
            return redirect(self.success_url)
        else:
            selected_product = '''
                           SELECT * FROM store_store_product WHERE "UPC" = %s
                    '''

            print('ya invalid')
            with connection.cursor() as cursor:
                cursor.execute(selected_product, [pk])
                selected_prod = cursor.fetchall()

            product = '''
                           SELECT * FROM store_product WHERE "id_product" = %s
                    '''

            with connection.cursor() as cursor:
                cursor.execute(product, [selected_prod[0][5]])
                prod = cursor.fetchall()

            prod_name, prod_characteristics = prod[0][1], prod[0][2]

            return render(request, template_name=self.template_name, context={
                'form': form,
                'pk': pk,
                'upc_prod': pk,
                'prod_name': prod_name,
                'prod_characteristics': prod_characteristics,
                'promotional_product': selected_prod[0][3],
                'selling_price': selected_prod[0][1]
            })


@method_decorator(login_required, name='dispatch')
class CheckListView(View):
    template_name = 'store/check/check-list.html'
    success_url = reverse_lazy('check-list')

    def get(self, request):
        form = CheckFilter(request.GET)
        employee_role = request.user.groups.first().name if request.user.groups.exists() else None

        query = """
            SELECT sc.check_number, sc.print_date, 
                ROUND((sc.sum_total) * (100 - COALESCE(scc.percent, 0)) / 100, 2) AS discounted_price, 
                sc.card_number_id, concat(se.empl_name, ' ', se.empl_surname) AS employee_name
            FROM store_check AS sc 
            INNER JOIN store_employee AS se ON sc.id_employee_id = se.id_employee
            LEFT JOIN store_customer_card AS scc ON sc.card_number_id = scc.card_number
        """
        query_params = []

        if form.is_valid():
            query += " WHERE 1=1"
            employee_id = form.cleaned_data.get("employee")

            if employee_role == 'cashier' or employee_id:
                if employee_role == 'cashier':
                    query += " AND se.id_employee = (SELECT id_employee FROM auth_user WHERE id = %s)"
                    query_params.append(request.user.id)

                if employee_id:
                    query += " AND se.id_employee = %s"
                    query_params.append(employee_id)

            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')

            if start_date:
                query += " AND sc.print_date >= %s"
                query_params.append(start_date)

            if end_date:
                query += " AND sc.print_date <= %s"
                query_params.append(end_date)
        else:
            query += " ORDER BY sc.print_date DESC;"

            with connection.cursor() as cursor:
                cursor.execute(query, query_params)
                checks = cursor.fetchall()

            checks_sum = sum([check[2] for check in checks])
            return render(request, template_name=self.template_name, context={
                'form': CheckFilter(),
                'checks': checks,
                'checks_sum': checks_sum
            })

        query += " ORDER BY sc.print_date DESC;"

        with connection.cursor() as cursor:
            cursor.execute(query, query_params)
            checks = cursor.fetchall()

        checks_sum = sum([check[2] for check in checks])
        return render(request, template_name=self.template_name, context={
            'form': form,
            'checks': checks,
            'checks_sum': checks_sum
        })


@method_decorator(login_required, name='dispatch')
class CheckCreateView(View):
    template_name = 'store/check/check-add.html'
    success_url = reverse_lazy('check-list')

    def get(self, request):
        selected_products = request.session.get('check_temporary_list')

        form = CheckDetailForm()
        all_products_query = """
        SELECT ssp."UPC", sp.product_name, ROUND(ssp.selling_price, 2), ssp.products_number 
        FROM store_store_product AS ssp
        INNER JOIN public.store_product AS sp 
        ON sp.id_product = ssp.id_product_id
        WHERE ssp.products_number != 0
        """

        params = []

        if selected_products and len(selected_products) > 0:
            selected_product_upcs = [product[0] for product in selected_products]
            all_products_query += 'AND ssp."UPC" NOT IN %s'
            params.append(tuple(selected_product_upcs))

        all_products_query += "ORDER BY sp.product_name;"

        with connection.cursor() as cursor:
            cursor.execute(all_products_query, params)
            all_products = cursor.fetchall()

        return render(request, template_name=self.template_name, context={
            'form': form,
            'selected_products': selected_products,
            'all_products': all_products
        })

    def post(self, request):
        selected_products = request.session.get('check_temporary_list')
        if selected_products:
            if request.POST.get('action') != 'delete':
                with transaction.atomic():
                    with connection.cursor() as cursor:
                        customer_card_number = request.POST.get('card_number', '')
                        if customer_card_number == '':
                            customer_card_number = None

                        sum_total = sum([float(product[2]) * int(product[3]) for product in selected_products])
                        current_cashier = request.user.id

                        employee_id_query = "SELECT id_employee FROM auth_user WHERE id = %s"

                        cursor.execute(employee_id_query, [current_cashier])
                        current_employee_id = cursor.fetchall()[0][0]

                        cursor.execute("SELECT check_number FROM store_check ORDER BY print_date DESC LIMIT 1")
                        check_count = int(cursor.fetchone()[0][3:])

                        check_count += 1

                        check_number = f'CHK{check_count:05d}'

                        check_insert_query = """
                        INSERT INTO store_check(check_number, print_date, sum_total, vat, card_number_id, id_employee_id) 
                        VALUES (%s, CURRENT_TIMESTAMP, %s, %s, %s, %s) 
                        """

                        cursor.execute(check_insert_query,
                                       [check_number, sum_total, sum_total * 0.2, customer_card_number,
                                        current_employee_id])

                        for product in selected_products:
                            product_upc = product[0]
                            product_price = product[2]
                            product_amount = product[3]

                            product_insert = """
                            INSERT INTO store_sale(product_number, selling_price, check_number_id, "UPC_id") 
                            VALUES (%s, %s, %s, %s)
                            """
                            cursor.execute(product_insert, [product_amount, product_price, check_number, product_upc])

                            store_product_update = """
                            UPDATE store_store_product SET products_number = products_number - %s WHERE "UPC" = %s
                            """
                            cursor.execute(store_product_update, [product_amount, product_upc])

            request.session['check_temporary_list'] = []

        return redirect(self.success_url)


@method_decorator(login_required, name='dispatch')
class CheckProductDetailView(View):
    template_name = 'store/check/check-product-detail.html'
    success_url = reverse_lazy('check-add')

    product_query = """
    SELECT ssp."UPC", sp.product_name, ROUND(ssp.selling_price, 2), ssp.products_number, sc.category_name 
    FROM store_product AS sp
    INNER JOIN public.store_store_product AS ssp ON sp.id_product = ssp.id_product_id 
    LEFT JOIN public.store_category AS sc ON sp.category_number_id = sc.category_number
    WHERE ssp."UPC" = %s;
    """

    def get(self, request, upc):
        check_temporary_list = request.session.get('check_temporary_list', [])

        form = CheckProductDetailForm()

        for product in check_temporary_list:
            if product[0] == upc:
                form = CheckProductDetailForm(initial={'quantity': product[3]})

        with connection.cursor() as cursor:
            cursor.execute(self.product_query, [upc])
            product = cursor.fetchall()[0]
            print(product)

        return render(request, template_name=self.template_name, context={
            'form': form,
            'product': product
        })

    def post(self, request, upc):
        form = CheckProductDetailForm(request.POST)

        if form.is_valid():
            selected_upc = request.POST.get('product_upc')
            selected_amount = request.POST.get('quantity')

            check_temporary_list = request.session.get('check_temporary_list', [])

            for product in check_temporary_list:
                if product[0] == selected_upc:
                    product[3] = selected_amount
                    request.session['check_temporary_list'] = check_temporary_list
                    return redirect(self.success_url)

            selected_product_query = f"""
            SELECT ssp."UPC", sp.product_name, ROUND(ssp.selling_price, 2), %s
            FROM store_store_product AS ssp
            INNER JOIN public.store_product AS sp
            ON sp.id_product = ssp.id_product_id
            WHERE ssp."UPC" = %s
            """

            with connection.cursor() as cursor:
                cursor.execute(selected_product_query, [int(selected_amount), selected_upc])
                selected_product = cursor.fetchall()[0]

            selected_product = list(selected_product)
            selected_product[2] = float(selected_product[2])
            check_temporary_list.append(selected_product)

            request.session['check_temporary_list'] = check_temporary_list

            return redirect(self.success_url)
        else:
            with connection.cursor() as cursor:
                cursor.execute(self.product_query, [upc])
                product = cursor.fetchall()[0]

            return render(request, template_name=self.template_name, context={
                'form': form,
                'product': product
            })


@method_decorator(login_required, name='dispatch')
class CheckDetailsView(View):
    template_name = 'store/check/check-detail.html'
    success_url = reverse_lazy('check-list')

    def get(self, request, pk):
        query = """
        SELECT sc.check_number, sc.print_date, ROUND(sc.sum_total, 2), ROUND((sc.sum_total) * (100 - 
        CASE 
            WHEN sc.card_number_id IS NULL THEN 0
            ELSE COALESCE(scc.percent, 0)
        END) / 100, 2) AS discounted_price, scc.percent, 
            sc.card_number_id, concat(se.empl_name, ' ', se.empl_surname) AS employee_name
        FROM store_check AS sc 
        LEFT JOIN store_employee AS se ON sc.id_employee_id = se.id_employee
        LEFT JOIN store_customer_card AS scc ON sc.card_number_id = scc.card_number
        WHERE sc.check_number = %s
        """

        all_products_query = """
        SELECT 
            ss."UPC_id", ps.product_name, ss.product_number, ROUND(ss.selling_price, 2)
        FROM
            store_sale AS ss
        INNER JOIN (SELECT sp.product_name, ssp."UPC" 
                    FROM store_product AS sp 
                    INNER JOIN store_store_product AS ssp 
                    ON sp.id_product = ssp.id_product_id) AS ps
        ON ps."UPC" = ss."UPC_id"
        WHERE
            ss.check_number_id = %s
        """

        with connection.cursor() as cursor:
            cursor.execute(all_products_query, [pk])
            all_products_in_check = cursor.fetchall()
            cursor.execute(query, [pk])
            check_header = cursor.fetchall()[0]
            print(check_header)

        return render(request, template_name=self.template_name, context={
            'all_products_in_check': all_products_in_check,
            'check_header': check_header
        })

    def post(self, request, pk):
        delete_check_query = """
        DELETE FROM store_check WHERE check_number = %s;
        """

        with connection.cursor() as cursor:
            cursor.execute(delete_check_query, [pk])

        return redirect(self.success_url)


class UserLoginView(View):
    template_name = 'registration/login.html'
    success_url = reverse_lazy('/products')

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('/products')
        form = UserLoginForm(request.POST or None)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        next = request.GET.get('next')
        form = UserLoginForm(request.POST or None)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if next:
                    return redirect(next)
                return redirect('/products')
        else:
            return render(request, self.template_name, {'form': form, 'msg': 'Invalid username or password'})


class UserRegisterView(View):
    template_name = 'registration/register.html'
    success_url = reverse_lazy('products')

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('/products')
        form = UserRegisterForm(request.POST or None)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        next = request.GET.get('next')
        form = UserRegisterForm(request.POST or None)
        if form.is_valid():
            selected_username = form.cleaned_data.get('username')
            selected_password = make_password(form.cleaned_data.get('password'))
            selected_empl = form.cleaned_data.get('empl')
            with connection.cursor() as cursor:
                cursor.execute("""SELECT empl_name, empl_surname FROM store_employee WHERE id_employee = %s""",
                               [selected_empl])
                employee = cursor.fetchall()[0]
                cursor.execute("""INSERT INTO auth_user(password, is_superuser, username, first_name, last_name, email,
                                                        is_staff, is_active, date_joined, id_employee) 
                                                        VALUES (%s, %s, %s, %s, %s, %s, %s,%s, CURRENT_TIMESTAMP, %s)
                               """,
                               [selected_password, False, selected_username, employee[0], employee[1], '',
                                selected_empl == 2, True
                                   , selected_empl])

            new_user = authenticate(username=selected_username, password=form.cleaned_data.get('password'))
            login(request, new_user)
            with connection.cursor() as cursor:
                cursor.execute("UPDATE auth_user SET id_employee = %s WHERE username = %s",
                               [form.cleaned_data.get('empl'), form.cleaned_data.get('username')])
                if 'CASH' in form.cleaned_data.get('empl'):
                    group_id = 1
                else:
                    group_id = 2
                cursor.execute("INSERT INTO auth_user_groups(user_id, group_id) VALUES (%s, %s)",
                               [new_user.id, group_id])
            if next:
                return redirect(next)
            return redirect('/')
        context = {
            'form': form,
        }
        return render(request, "registration/register.html", context)


def logout_view(request):
    logout(request)
    return redirect('/accounts/login')


def user_profile(request):
    with connection.cursor() as cursor:
        cursor.execute("""SELECT e.* 
                       FROM auth_user a JOIN store_employee e ON a.id_employee = e.id_employee
                       WHERE a.id = %s """, [request.user.id])
        data = cursor.fetchall()
        employee = dict()
        employee['id'] = data[0][0]
        employee['employee_surname'] = data[0][1]
        employee['employee_name'] = data[0][2]
        employee['employee_patronymic'] = data[0][3]
        employee['employee_role'] = data[0][4]
        employee['employee_salary'] = data[0][5]
        employee['employee_date_of_birth'] = data[0][6]
        employee['employee_date_of_start'] = data[0][7]
        employee['employee_phone_number'] = data[0][8]
        employee['employee_city'] = data[0][9]
        employee['employee_street'] = data[0][10]
        employee['employee_zip_code'] = data[0][11]
        return render(request, "profile/profile.html", {"employee": employee})


@method_decorator(login_required, name='dispatch')
class StatisticsTab(View):
    def get(self, request):
        form = StatsDateOptions(request.GET)
        if form.is_valid():
            print("VALIDDDDDD")
        else:
            print(form.errors)

        not_purchased_products_date = form.cleaned_data.get('products_date') if form.is_valid() else None
        not_active_customers_date = form.cleaned_data.get('customers_date') if form.is_valid() else None
        selected_category = form.cleaned_data.get('category_name') if form.is_valid() else None
        not_purchased_products_date = not_purchased_products_date or date(1900, 1, 1)
        not_active_customers_date = not_active_customers_date or date(1900, 1, 1)

        with connection.cursor() as cursor:
            # Query for top 10 products by revenue
            cursor.execute("""
                SELECT p.id_product, p.product_name, SUM(s.selling_price * s.product_number) AS total_revenue
                FROM store_product p JOIN store_store_product sp ON p.id_product = sp.id_product_id
                                     JOIN store_sale s ON sp."UPC" = s."UPC_id"
                GROUP BY 1, 2
                ORDER BY total_revenue DESC LIMIT 10
                        """)
            top_10_products_with_biggest_revenue = cursor.fetchall()
            chart_1_labels = [row[1] for row in top_10_products_with_biggest_revenue]
            chart_1_values = [float(row[2]) for row in top_10_products_with_biggest_revenue]

            # Query for products that were not purchased within a specific date range
            cursor.execute("""
                SELECT DISTINCT p.product_name
                FROM store_product p JOIN store_store_product sp ON p.id_product = sp.id_product_id
                                     JOIN store_sale s ON sp."UPC" = s."UPC_id"
                WHERE sp."UPC" NOT IN ( 
                    SELECT "UPC_id"
                    FROM store_sale s JOIN store_check c ON s.check_number_id = c.check_number
                    WHERE c.print_date NOT IN ( 
                        SELECT print_date
                        FROM store_check
                        WHERE print_date < %s
                    )
                )
            """, [not_purchased_products_date])
            not_purchased_products_within_date = cursor.fetchall()
            list_1 = [row[0] for row in not_purchased_products_within_date]

            # Query for top 5 most productive cashiers
            cursor.execute("""
            SELECT CONCAT(se.empl_name, ' ', se.empl_surname) AS cashier_name,
                   ROUND(SUM(sc.sum_total) * (100 - COALESCE(AVG(CASE
                                                                       WHEN sc.card_number_id IS NULL THEN 0
                                                                       ELSE scc.percent
                                                                   END), 0)
                                               ) / 100, 2) AS discounted_price
            FROM store_check AS sc
            LEFT JOIN store_employee AS se ON sc.id_employee_id = se.id_employee
            LEFT JOIN store_customer_card AS scc ON sc.card_number_id = scc.card_number
            GROUP BY se.empl_name, se.empl_surname
            ORDER BY discounted_price DESC
            LIMIT 5;
            """)
            most_productive_cashiers = cursor.fetchall()
            chart_2_labels = [row[0] for row in most_productive_cashiers]
            chart_2_values = [float(row[1]) for row in most_productive_cashiers]

            # Query for inactive customers within a specific date range
            cursor.execute("""
                SELECT DISTINCT CONCAT(scc.cust_name, ' ', scc.cust_surname) AS customer_name, (
                    SELECT id_employee_id 
                    FROM store_check sc2
                    LEFT JOIN store_employee se ON se.id_employee = sc2.id_employee_id
                    WHERE sc2.id_employee_id = sc.id_employee_id
                    ORDER BY sc2.print_date DESC LIMIT 1
                )
                FROM store_check sc
                RIGHT JOIN store_customer_card scc ON scc.card_number = sc.card_number_id
                WHERE scc.card_number NOT IN (
                        SELECT DISTINCT c.card_number_id
                        FROM store_check c
                        WHERE c.print_date NOT IN (
                                SELECT print_date
                                FROM store_check
                                WHERE print_date < %s  
                        ) AND c.card_number_id IS NOT NULL
                );
            """, [not_active_customers_date])
            not_active_customers_within_date = cursor.fetchall()
            list_2 = [f"{row[0]} - {row[1]}" for row in not_active_customers_within_date]

            # query to find all clients which never bought products at a discount
            cursor.execute('''
                        SELECT card_number, CONCAT(cust_surname, ' ',cust_name) AS full_name, phone_number, 
                           CONCAT(street, ', ', city, ' ', zip_code) as address, percent as discount
                           FROM store_customer_card
                           WHERE card_number NOT IN (SELECT card_number_id 
                                                     FROM store_check AS ch
                                                     WHERE check_number IN (SELECT check_number_id 
                                                                      FROM store_sale
                                                                      WHERE "UPC_id" NOT IN (
                                                                                      SELECT "UPC"
                                                                                      FROM store_store_product
                                                                                      WHERE promotional_product IS False
                                                                                          )
                                                                      ) AND card_number_id IS NOT NULL
                                            ) AND card_number IN (SELECT card_number_id FROM store_check)
     
                ''')
            gold_clients = cursor.fetchall()
            cursor.execute('''SELECT * FROM store_category''')
            if selected_category is None:
                list_3 = None
            else:
                selected_category = selected_category.category_name
                print(selected_category)
                cursor.execute('''
                      SELECT sp.product_name, COUNT(*) as number_purchases
                      FROM store_product AS sp 
                      INNER JOIN store_category AS sc ON sp.category_number_id = sc.category_number
                      INNER JOIN store_store_product AS ssp ON sp.id_product = ssp.id_product_id
                      INNER JOIN store_sale AS ss ON ssp."UPC" = ss."UPC_id"
                      WHERE sc.category_name = %s
                      GROUP BY sp.product_name
                      ORDER BY number_purchases DESC LIMIT 5
                ''', [selected_category])
                top_product = cursor.fetchall()
                list_3 = [f"{row[0]} - {row[1]} purchases" for row in top_product]
                print(list_3)

        return render(request, 'store/statistics/statistics.html', {
            'form': form,
            'chart_1_labels': chart_1_labels,
            'chart_1_values': chart_1_values,
            'chart_2_labels': chart_2_labels,
            'chart_2_values': chart_2_values,
            'list_1': list_1,
            'list_2': list_2,
            'list_3': list_3,
            'gold_clients': gold_clients
        })


@login_required
def password_reset(request):
    success_url = reverse_lazy("user-profile")
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            new_password = form.cleaned_data.get('new_password1')
            with connection.cursor() as cursor:
                cursor.execute("UPDATE auth_user SET password = %s WHERE id = %s",
                               [make_password(new_password), request.user.id])
            user = authenticate(username=request.user.username, password=new_password)
            if user is not None:
                login(request, user)
                return redirect(success_url)
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, 'registration/password-reset.html', {'form': form})
