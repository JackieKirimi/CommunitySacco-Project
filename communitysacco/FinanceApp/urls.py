from django.urls import path
from . import views

urlpatterns = [
    path('savings/', views.savings, name='savings'),
    path('index/', views.index, name='index'),
    path('loans/', views.loans, name='loans'),
    path('transactions/', views.transactions, name='transactions'),
    path('admin/login/', views.admin_login, name='admin-login'),
    path('admin/loans/', views.loan_approval_dashboard, name='loan-approval-dashboard'),
    path('payment/',views.mpesaPayment,name='mpesaPayment'),
]
