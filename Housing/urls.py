from django.urls import path

from . import views

urlpatterns = [
    path('', views.listings, name='listings'),
    path('search', views.search, name='search'),
    path('listing-details/<int:listing_id>', views.detail, name='listing-details'),
    path('checkout/<int:listing_id>/', views.create_checkout_session, name='checkout'),
    path('success/', views.success, name='success'),


]