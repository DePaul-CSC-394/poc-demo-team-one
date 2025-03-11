from django.urls import path
from . import views  

urlpatterns = [
    path('', views.roommates, name='roommates'),  
    path('roommatesDashboard/', views.roommatesDashboard, name='roommatesDashboard'),
    path("questionnaire/", views.questionnaire_view, name="questionnaire"),
    path("edit-responses/", views.editResponses, name="editResponses")
]
