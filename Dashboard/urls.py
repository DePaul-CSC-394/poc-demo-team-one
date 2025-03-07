from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('add_listing/', views.add_listing, name='add_listing'),
    path('add_supplies/', views.add_supplies, name='add_supplies'),
    path('approve_or_deny', views.approve_or_deny, name='approve_or_deny'),
    path('delete-listing/<int:listing_id>/', views.delete_listing, name='delete_listing'),
    path('delete-supply/<int:supply_id>/', views.delete_supplies, name='delete_supply'),
    path('review-supply/<int:listing_id>/', views.reviewSupply, name='review-supply'),
    path('review-home/<int:listing_id>/', views.reviewHome, name='review-home'),
]