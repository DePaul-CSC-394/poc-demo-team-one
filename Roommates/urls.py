from django.urls import path
from . import views  

urlpatterns = [
    path('roommates/', views.roommates, name='roommates'),  
    path('roommatesDashboard/', views.roommatesDashboard, name='roommatesDashboard')
]
