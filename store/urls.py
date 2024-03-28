from django.urls import path
from . import views

urlpatterns = [
    # Empty URL pattern
    path('', views.index, name='index'),

    # For employee URLs
    path('employee/', views.EmployeeListView.as_view(), name='employee_list'),
    path('employee/add/', views.EmployeeCreateView.as_view(), name='employee_add'),
    path('employee/<int:pk>', views.EmployeeUpdateView.as_view(), name='employee-detail'),

    # For clients URLs
    path('clients/', views.ClientListView.as_view(), name='client_list'),
    path('clients/add/', views.ClientCreateView.as_view(), name='client_add'),
    path('clients/<int:pk>', views.ClientUpdateView.as_view(), name='card-number-details'),

    # For categories URLs
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/add/', views.CategoryCreateView.as_view(), name='category_add'),
    path('categories/<int:pk>', views.CategoryUpdateView.as_view(), name='category-detail'),

    # For products URLs
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/add/', views.ProductCreateView.as_view(), name='product_add'),
    path('products/<int:pk>', views.ProductDetailView.as_view(), name='product-detail'),

    # For store-products URLs
    path('store-products/', views.StoreProductListView.as_view(), name='store_product_list'),
    path('store-products/add/', views.StoreProductCreateView.as_view(), name='store_product_add'),
    path('store-products/<int:pk>', views.StoreProductUpdateView.as_view(), name='store-product-details'),

    # For check URLs
    path('check/', views.CheckListView.as_view(), name='check_list'),
    path('check-details/', views.CheckDetailsView.as_view(), name='check_details'),
]
