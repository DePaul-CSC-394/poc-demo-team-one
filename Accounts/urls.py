from django.urls import path

from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('signout/', views.signout, name='signout'),
    path('profile/', views.profile, name='profile'),
    path('save-profile', views.saveProfile, name='save-profile'),
    path('view-profile/<int:user_id>', views.staticProfile, name='view-profile'),
]