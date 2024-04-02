from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db import connection
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, reverse, redirect, HttpResponseRedirect
from django.views import View
from django.contrib import messages
from django.urls import reverse_lazy
from .forms import ProductFilterForm, ProductDetailForm, EmployeeFilterForm, EmployeeDetailForm, \
    ClientFilterForm, ClientDetailForm, CategoryDetailForm, UserLoginForm, UserRegisterForm, CheckProductDetailForm, \
    CheckDetailForm


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
        form = EmployeeDetailForm(request.POST, initial={'pk': pk})
        print(form.errors)
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
                print("This discount ", discount)
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
            'clients': clients
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
        delete = ('DELETE FROM store_customer_card WHERE card_number = %s')

        with connection.cursor() as cursor:
            cursor.execute(delete, [pk])

        messages.success(request, 'Client deleted successfully')
        return redirect(self.success_url)

    def update_client(self, request, pk):
        form = ClientDetailForm(request.POST)
        print(form.errors)
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
        delete = 'DELETE FROM store_category WHERE category_number = %s'

        with connection.cursor() as cursor:
            cursor.execute(delete, [pk])

        messages.success(request, 'Category deleted successfully')
        return redirect(self.success_url)

    def update_category(self, request, pk):
        form = CategoryDetailForm(request.POST, initial={"pk": pk})
        print(form.errors)
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


class StoreProductListView(View):
    pass


class StoreProductCreateView(View):
    pass


class StoreProductUpdateView(View):
    pass


@method_decorator(login_required, name='dispatch')
class CheckListView(View):
    template_name = 'store/check/check-list.html'

    def get(self, request):
        employee_role = str(request.user.groups.all()[0])
        auth_user_id = request.user.id
        query = """
        SELECT sc.check_number, sc.print_date, ROUND((sc.sum_total) * (100 - scc.percent) / 100, 2)  AS discounted_price, 
            sc.card_number_id, concat(se.empl_name, ' ', se.empl_surname) 
        FROM store_check AS sc 
        INNER JOIN store_employee AS se ON sc.id_employee_id = se.id_employee
        INNER JOIN store_customer_card AS scc ON sc.card_number_id = scc.card_number
        """

        if employee_role == 'cashier':
            query += "WHERE se.id_employee = %s;"

            employee_id_query = "SELECT id_employee FROM auth_user WHERE id = %s"

            with connection.cursor() as cursor:
                cursor.execute(employee_id_query, [auth_user_id])
                employee_id = cursor.fetchall()
                cursor.execute(query, [employee_id[0]])
                checks = cursor.fetchall()

        else:
            with connection.cursor() as cursor:
                cursor.execute(query)
                checks = cursor.fetchall()

        return render(request, template_name=self.template_name, context={
            'checks': checks
        })


@method_decorator(login_required, name='dispatch')
class CheckCreateView(View):
    template_name = 'store/check/check-add.html'
    success_url = reverse_lazy('с-list')

    def get(self, request):
        form = CheckDetailForm()
        all_products_query = """
        SELECT sp.id_product, sp.product_name, ROUND(ssp.selling_price, 2), ssp.products_number 
        FROM store_store_product AS ssp
        INNER JOIN public.store_product AS sp 
        ON sp.id_product = ssp.id_product_id
        """

        with connection.cursor() as cursor:
            cursor.execute(all_products_query),
            all_products = cursor.fetchall()

        return render(request, template_name=self.template_name, context={
            'form': form,
            'all_products': all_products
        })

    def post(self, request):
        selected_upc = request.POST.get('product_upc', None)
        selected_amount = request.POST.get('quantity', None)

        check_temporary_list = request.session.get('check_temporary_list', [])

        check_temporary_list.append((selected_upc, selected_amount))

        request.session['check_temporary_list'] = check_temporary_list

        # зроби запит, щоб витягалися всі дані про збережені продукти, та за натискання кнопки
        # "add check" контекст видалявся, можна ще додати іншу кнопку чисто з "clean check"
        form = CheckDetailForm()
        all_products_query = """
        SELECT sp.id_product, sp.product_name, ROUND(ssp.selling_price, 2), ssp.products_number 
        FROM store_store_product AS ssp
        INNER JOIN public.store_product AS sp 
        ON sp.id_product = ssp.id_product_id
        """

        with connection.cursor() as cursor:
            cursor.execute(all_products_query),
            all_products = cursor.fetchall()

        return render(request, template_name=self.template_name, context={
            'form': form,
            'selected_products': None,
            'all_products': all_products
        })



class CheckProductDetailView(View):
    template_name = 'store/check/check-product-detail.html'

    def get(self, request, upc):
        form = CheckProductDetailForm()

        product_query = """
        SELECT sp.id_product, sp.product_name, ROUND(ssp.selling_price, 2), ssp.products_number, sc.category_name FROM store_product AS sp
        INNER JOIN public.store_store_product AS ssp ON sp.id_product = ssp.id_product_id 
        INNER JOIN public.store_category AS sc ON sp.category_number_id = sc.category_number
        WHERE sp.id_product = %s;
        """

        with connection.cursor() as cursor:
            cursor.execute(product_query, [upc])
            product = cursor.fetchall()

        return render(request, template_name=self.template_name, context={
            'form': form,
            'product': product
        })

    # def post(self, request, upc):
    #
    #     return render(request, template_name=self.template_name, context={
    #         'form': form,
    #     })
        # if form.is_valid():
        #     request.session.get('check_temp_list', [])

@method_decorator(login_required, name='dispatch')
class CheckDetailsView(View):
    template_name = 'store/check/check-detail.html'

    def get(self, request, pk):
        query = """
        SELECT sc.check_number, sc.print_date, ROUND((sc.sum_total) * (100 - scc.percent) / 100, 2)  AS discounted_price, 
            sc.card_number_id, concat(se.empl_name, ' ', se.empl_surname) 
        FROM store_check AS sc 
        INNER JOIN store_employee AS se ON sc.id_employee_id = se.id_employee
        INNER JOIN store_customer_card AS scc ON sc.card_number_id = scc.card_number
        WHERE sc.check_number = %s
        """

        all_products_query = """
        SELECT
            ss."UPC_id",
            upc_pn.product_name,
            ss.product_number,
            ROUND(ss.selling_price, 2),
            COALESCE(cp.percent, 0) AS percent,
            ROUND((ss.product_number * ss.selling_price) * (100 - percent) / 100, 2) AS discounted_price
        FROM store_sale AS ss
        INNER JOIN (SELECT ssp."UPC", sp.product_name
                    FROM store_store_product AS ssp
                    INNER JOIN store_product AS sp
                    ON ssp.id_product_id = sp.id_product
        ) AS upc_pn
        ON ss."UPC_id" = upc_pn."UPC"
        LEFT JOIN (SELECT sc.check_number, scc.percent
                    FROM store_check AS sc
                    INNER JOIN store_customer_card AS scc
                    ON sc.card_number_id = scc.card_number
        ) AS cp
        ON ss.check_number_id = cp.check_number
        WHERE ss.check_number_id = %s;
        """

        with connection.cursor() as cursor:
            cursor.execute(all_products_query, [pk])
            all_products_in_check = cursor.fetchall()
            cursor.execute(query, [pk])
            check_header = cursor.fetchall()

        return render(request, template_name=self.template_name, context={
            'all_products_in_check': all_products_in_check,
            'check_header': check_header
        })


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
        print(data)
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
