from django.db import connection
from django.shortcuts import render, reverse, redirect, HttpResponseRedirect
from django.views import View
from django.contrib import messages
from django.urls import reverse_lazy

from .models import Employee, Category, Product, Store_Product, Customer_Card, Check, Sale
from .forms import ProductFilterForm, ProductAddForm, ProductEditForm, EmployeeFilterForm, EmployeeAddForm, \
    EmployeeEditForm


# Create your views here.

def index(request):
    return redirect('product_list')


class EmployeeListView(View):
    template_name = 'store/employee-list.html'

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
                print("This role ", selected_role)
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


class EmployeeCreateView(View):
    template_name = 'store/employee-add.html'
    success_url = reverse_lazy('employee_list')  # Assuming 'product_list' is the name of your product list URL

    def get(self, request):
        return render(request, template_name=self.template_name, context={
            'form': EmployeeAddForm()
        })

    def post(self, request):
        form = EmployeeAddForm(request.POST)
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
            selected_role = form.cleaned_data.get('employee_role')
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


class EmployeeDetailView(View):
    template_name = 'store/employee-detail.html'
    success_url = reverse_lazy('employee_list')

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

        form = EmployeeEditForm(initial={
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
        })

    def post(self, request, pk):
        if request.POST.get('action') == 'delete':
            return self.delete_employee(request, pk)
        else:
            return self.update_employee(request, pk)

    def delete_employee(self, request, pk):
        delete = 'DELETE FROM store_employee WHERE id_employee = %s'

        with connection.cursor() as cursor:
            cursor.execute(delete, [pk])

        messages.success(request, 'Employee deleted successfully')
        return redirect(self.success_url)

    def update_employee(self, request, pk):
        form = EmployeeEditForm(request.POST)
        print(form.errors)
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
            selected_role = form.cleaned_data.get('employee_role')
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
                    empl_patronymic = %s, empl_role = %s, salary = %s,
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
                'pk': pk
            })


class ClientListView(View):
    pass


class ClientCreateView(View):
    pass


class ClientUpdateView(View):
    pass


class CategoryListView(View):
    pass


class CategoryCreateView(View):
    pass


class CategoryUpdateView(View):
    pass


class ProductListView(View):
    template_name = 'store/product-list.html'

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


class ProductCreateView(View):
    template_name = 'store/product-add.html'
    success_url = reverse_lazy('product_list')

    def get(self, request):
        return render(request, template_name=self.template_name, context={
            'form': ProductAddForm()
        })

    def post(self, request):
        form = ProductAddForm(request.POST)
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


class ProductDetailView(View):
    template_name = 'store/product-detail.html'
    success_url = reverse_lazy('product_list')

    def get(self, request, pk):
        query = '''
            SELECT * FROM store_product WHERE id_product = %s
            '''
        with connection.cursor() as cursor:
            cursor.execute(query, [pk])
            product = cursor.fetchall()

        product_name, characteristics, category = product[0][1], product[0][2], product[0][3]

        form = ProductEditForm(initial={
            'product_name': product_name,
            'characteristics': characteristics,
            'category': category
        })

        return render(request, template_name=self.template_name, context={
            'form': form,
            'pk': pk,
        })

    def post(self, request, pk):
        if request.POST.get('action') == 'delete':
            return self.delete_product(request, pk)
        else:
            return self.update_product(request, pk)

    def delete_product(self, request, pk):
        delete = 'DELETE FROM store_product WHERE id_product = %s'

        with connection.cursor() as cursor:
            cursor.execute(delete, [pk])

        messages.success(request, 'Product added successfully')
        return redirect(self.success_url)

    def update_product(self, request, pk):
        form = ProductEditForm(request.POST)

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


class StoreProductListView(View):
    pass


class StoreProductCreateView(View):
    pass


class StoreProductUpdateView(View):
    pass


class CheckListView(View):
    pass


class CheckDetailsView(View):
    pass
