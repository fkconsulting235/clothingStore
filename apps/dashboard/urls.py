from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views

app_name = 'dashboard'

urlpatterns = [
    path('login/', LoginView.as_view(
        template_name='dashboard/login.html', redirect_authenticated_user=True,
    ), name='login'),
    path('logout/', LogoutView.as_view(next_page='dashboard:login'), name='logout'),

    path('', views.home, name='home'),

    path('prendas/', views.product_list, name='product_list'),
    path('prendas/nueva/', views.product_form, name='product_create'),
    path('prendas/<int:pk>/editar/', views.product_form, name='product_edit'),
    path('prendas/<int:pk>/eliminar/', views.product_delete, name='product_delete'),

    path('categorias/', views.category_list, name='category_list'),
    path('categorias/nueva/', views.category_form, name='category_create'),
    path('categorias/<int:pk>/editar/', views.category_form, name='category_edit'),
    path('categorias/<int:pk>/eliminar/', views.category_delete, name='category_delete'),

    path('reservas/', views.reservation_list, name='reservation_list'),
    path('pedidos/', views.order_list, name='order_list'),
    path('pedidos/<int:pk>/marcar-pagado/', views.order_mark_paid, name='order_mark_paid'),
    path('pedidos/<int:pk>/deshacer-pagado/', views.order_undo_paid, name='order_undo_paid'),
    path('pedidos/<int:pk>/rechazar/', views.order_reject, name='order_reject'),

    path('cuentas-bancarias/', views.bank_account_list, name='bank_account_list'),
    path('cuentas-bancarias/nueva/', views.bank_account_form, name='bank_account_create'),
    path('cuentas-bancarias/<int:pk>/editar/', views.bank_account_form, name='bank_account_edit'),
    path('cuentas-bancarias/<int:pk>/eliminar/', views.bank_account_delete, name='bank_account_delete'),
]
