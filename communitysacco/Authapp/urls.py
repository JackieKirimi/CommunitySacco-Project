from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('login/', views.loginUser, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('register/', views.registerUser, name='register'),
    path('profile/', views.profile, name='profile'),
    path('values/', views.app_values, name='app-values'),
    path('chatbot-assistant/', views.chatbot_assistant, name='chatbot-assistant'),
    
]
