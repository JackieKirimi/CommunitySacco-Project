from django.shortcuts import render , redirect
from django.contrib.auth.decorators import login_required


# Create your views here.
@login_required
def home(request):
    return render(request, "Saccoapp/home.html")

@login_required
def savings(request):
    return render(request, "Saccoapp/savings.html")

@login_required
def loans(request):
    return render(request, "Saccoapp/loans.html")

@login_required
def transactions(request):
    return render(request, "Saccoapp/transactions.html")

