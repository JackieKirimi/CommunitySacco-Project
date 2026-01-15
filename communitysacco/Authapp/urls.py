from django.urls import path, include
from . import views
from django.urls import path


urlpatterns = [
    path('home', views.home, name='home'),
    path('', views.home, name='home'),
    path('login/', views.loginUser, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('register/', views.registerUser, name='register'),
    path('profile/', views.profile, name='profile'),
    
]