from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('add_listing/', views.add_listing, name='add_listing'),
    path('approve_or_deny', views.approve_or_deny, name='approve_or_deny'),
    path('delete-listing/<int:listing_id>/', views.delete_listing, name='delete_listing'),
]