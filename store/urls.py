from django.urls import path, include
from . import views

urlpatterns = [
    # Empty URL pattern
    path('', views.index, name='index'),

    # For employee URLs
    path('employee/', views.EmployeeListView.as_view(), name='employee-list'),
    path('employee/add/', views.EmployeeCreateView.as_view(), name='employee-add'),
    path('employee/<str:pk>', views.EmployeeDetailView.as_view(), name='employee-detail'),

    # For clients URLs
    path('clients/', views.ClientListView.as_view(), name='client-list'),
    path('clients/add/', views.ClientCreateView.as_view(), name='client-add'),
    path('clients/<str:pk>', views.ClientUpdateView.as_view(), name='client-detail'),

    # For categories URLs
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('categories/add/', views.CategoryCreateView.as_view(), name='category-add'),
    path('categories/<int:pk>', views.CategoryUpdateView.as_view(), name='category-detail'),

    # For products URLs
    path('products/', views.ProductListView.as_view(), name='product-list'),
    path('products/add/', views.ProductCreateView.as_view(), name='product-add'),
    path('products/<int:pk>', views.ProductDetailView.as_view(), name='product-detail'),

    # For store-products URLs
    path('store-products/', views.StoreProductListView.as_view(), name='store-product-list'),
    path('store-products/add/', views.StoreProductCreateView.as_view(), name='store-product-add'),
    path('store-products/<str:pk>', views.StoreProductUpdateView.as_view(), name='store-product-details'),
    path('store-products/<str:pk>/promotional', views.StorePromotionalProductCreateView.as_view(),
         name='store-product-add-promotional'),


    # For check URLs
    path('check/', views.CheckListView.as_view(), name='check-list'),
    path('check/add/', views.CheckCreateView.as_view(), name='check-add'),
    path('check/<str:pk>', views.CheckDetailsView.as_view(), name='check-details'),
    path('check/add/<str:upc>', views.CheckProductDetailView.as_view(), name='check-product-detail'),

    path('accounts/login/', views.UserLoginView.as_view(), name='user-login'),
    path('accounts/register/', views.UserRegisterView.as_view(), name='user-register'),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('accounts/profile/', views.user_profile, name='user-profile'),

    path('statistics/', views.StatisticsTab.as_view(), name='statistics')
]
