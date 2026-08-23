from django.urls import path

from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.home, name='home'),
    path('buscar/', views.search, name='search'),
    path('categoria/<slug:slug>/', views.category_detail, name='category'),
    path('prenda/<slug:slug>/', views.product_detail, name='product_detail'),
]
