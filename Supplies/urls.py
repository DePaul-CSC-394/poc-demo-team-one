from django.urls import path

from . import views

urlpatterns = [
    path('Supplies/', views.supplies, name='supplies'),
    path('supply-details/<int:listing_id>', views.detail, name='supply-details'),
    path('create-checkout-session-supply/<int:listing_id>/', views.create_checkout_session, name='checkout'),
    path('success-supplies/', views.success, name='success'),
    path('searchSupplies', views.search, name='searchSupplies'),
]