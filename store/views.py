from django.shortcuts import render, reverse, HttpResponseRedirect
from django.views import View

from .models import Employee, Category, Product, Store_Product, Customer_Card, Check, Sale


# Create your views here.

def index(request):
    pass


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
