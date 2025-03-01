from django.urls import path

from . import views

urlpatterns = [
    #path('', views., name=''), TBD - supply listings page
    path('supply-details/<int:listing_id>', views.detail, name='supply-details'),
]