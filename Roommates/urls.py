from django.urls import path
from . import views  # Ensure you import views

urlpatterns = [
    path('roommates/', views.roommates, name='roommates'),  # Use correct function
]
