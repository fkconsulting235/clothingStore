from django.urls import path

from . import views

app_name = 'orders'

urlpatterns = [
    path('comprar/<int:variant_id>/', views.start_checkout, name='checkout'),
    path('<int:pk>/pagar/', views.pay, name='pay'),
    path('<int:pk>/en-revision/', views.pending_review, name='pending_review'),

    path('carrito/', views.cart_detail, name='cart_detail'),
    path('carrito/agregar/<int:variant_id>/', views.add_to_cart, name='cart_add'),
    path('carrito/actualizar/<int:variant_id>/', views.cart_update, name='cart_update'),
    path('carrito/quitar/<int:variant_id>/', views.cart_remove, name='cart_remove'),
]
