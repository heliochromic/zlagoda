from django.shortcuts import render, reverse, redirect, HttpResponseRedirect
from django.views import View
from django.db import connection

from .models import Employee, Category, Product, Store_Product, Customer_Card, Check, Sale
from .forms import ProductFilterForm


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

        if form.is_valid():

            product_name = form.cleaned_data.get('search')
            selected_category = form.cleaned_data.get('category')

            print(f"""

            ТИ ДЕБІЛ
            {product_name} 
            {selected_category} 


            """)
            query = f'''
                SELECT p.id_product, p.product_name, p.characteristics, c.category_name
                FROM store_product AS p
                INNER JOIN store_category AS c ON p.category_number_id = c.category_number
                WHERE c.category_name = %s
                OR p.product_name LIKE %s
            '''
            products = Product.objects.raw(query, [selected_category, f'{product_name}%'])

        else:
            query = f'''
                SELECT p.id_product, p.product_name, p.characteristics, c.category_name
                FROM store_product AS p
                INNER JOIN store_category AS c ON p.category_number_id = c.category_number
            '''
            products = Product.objects.raw(query)

        print(products.query)

        return render(request, template_name=self.template_name, context={
            'form': form,
            'products': products
        })

    def post(self, request):
        pass


class ProductCreateView(View):
    pass


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
