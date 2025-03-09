from django.urls import path
from . import views 


urlpatterns = [
    path('roommatesDashboard/', views.roommatesDashboard, name='roommatesDashboard')
]
