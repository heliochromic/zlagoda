from django.urls import path
from . import views

urlpatterns = [
    # Empty URL pattern
    path('', views.index, name='index'),

    # For employee URLs
    path('employee/', views.EmployeeListView.as_view(), name='employee_list'),
    path('employee/add/', views.EmployeeCreateView.as_view(), name='employee_add'),
    path('employee/<uuid:pk>/edit/', views.EmployeeUpdateView.as_view(), name='employee_edit'),

    # For clients URLs
    path('clients/', views.ClientListView.as_view(), name='client_list'),
    path('clients/add/', views.ClientCreateView.as_view(), name='client_add'),
    path('clients/<uuid:pk>/edit/', views.ClientUpdateView.as_view(), name='client_edit'),

    # For categories URLs
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/add/', views.CategoryCreateView.as_view(), name='category_add'),
    path('categories/<uuid:pk>/edit/', views.CategoryUpdateView.as_view(), name='category_edit'),

    # For products URLs
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/add/', views.ProductCreateView.as_view(), name='product_add'),
    path('products/<uuid:pk>/edit/', views.ProductUpdateView.as_view(), name='product_edit'),

    # For store-products URLs
    path('store-products/', views.StoreProductListView.as_view(), name='store_product_list'),
    path('store-products/add/', views.StoreProductCreateView.as_view(), name='store_product_add'),
    path('store-products/<uuid:pk>/edit/', views.StoreProductUpdateView.as_view(), name='store_product_edit'),

    # For check URLs
    path('check/', views.CheckListView.as_view(), name='check_list'),
    path('check-details/', views.CheckDetailsView.as_view(), name='check_details'),
]
