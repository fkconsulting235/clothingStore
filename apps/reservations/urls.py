from django.urls import path

from . import views

app_name = 'reservations'

urlpatterns = [
    path('reservar/<int:variant_id>/', views.create_reservation, name='create'),
    path('confirmacion/<int:pk>/', views.reservation_confirmation, name='confirmation'),
    path('buscar/', views.lookup_reservation, name='lookup'),
]
