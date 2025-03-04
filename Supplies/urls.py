from django.urls import path

from . import views

urlpatterns = [
    #path('', views., name=''), TBD - supply listings page
    path('Supplies/', views.supplies, name='supplies'),
    path('supply-details/<int:listing_id>', views.detail, name='supply-details'),
    path('create-checkout-session/<int:listing_id>/', views.create_checkout_session, name='checkout'),
    path('success/', views.success, name='success'),
]