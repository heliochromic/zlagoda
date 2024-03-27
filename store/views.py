from django.db import connection
from django.shortcuts import render, reverse, redirect, HttpResponseRedirect
from django.views import View
from django.contrib import messages
from django.urls import reverse_lazy

from .models import Employee, Category, Product, Store_Product, Customer_Card, Check, Sale
from .forms import ProductFilterForm, ProductAddForm


# Create your views here.

def index(request):
    return redirect('product_list')


class EmployeeListView(View):
    pass


class EmployeeCreateView(View):
    pass


class EmployeeUpdateView(View):
    pass


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
                cursor.execute(query, query_params)
                products = cursor.fetchall()

        else:
            with connection.cursor() as cursor:
                cursor.execute(query)
                products = cursor.fetchall()

        print(products)

        return render(request, template_name=self.template_name, context={
            'form': form,
            'products': products
        })


class ProductCreateView(View):
    template_name = 'store/product-add.html'
    success_url = reverse_lazy('product_list')  # Assuming 'product_list' is the name of your product list URL

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


class ProductUpdateView(View):
    pass


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
