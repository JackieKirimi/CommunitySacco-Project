from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate ,login ,logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.http import HttpResponse
from FinanceApp.models import Transaction, UserLoanLimit


# Create your views here.
def home(request):
    context = {}
    if request.user.is_authenticated:
        latest_loan = request.user.loan_requests.first()
        loan_status = latest_loan.get_status_display() if latest_loan else "None"
        total_saved = request.user.savings_records.aggregate(total=Sum("amount"))["total"] or 0
        pending_transactions = request.user.transactions.filter(status=Transaction.STATUS_PENDING).count()
        loan_limit_obj = UserLoanLimit.objects.filter(user=request.user).first()
        loan_limit = loan_limit_obj.amount if loan_limit_obj and loan_limit_obj.amount is not None else "None"

        context.update(
            {
                "loan_status": loan_status,
                "total_saved": total_saved,
                "pending_transactions": pending_transactions,
                "loan_limit": loan_limit,
            }
        )
    return render(request, 'Authapp/home.html', context)

def loginUser(request):
    selected_role = request.GET.get("role", "user").lower()
    if selected_role not in ["user", "admin"]:
        selected_role = "user"

    if request.method=='POST':
        username =request.POST.get('username', '').strip().lower()
        password =request.POST.get('password', '')
        selected_role = request.POST.get("account_type", "user").lower()
        if selected_role not in ["user", "admin"]:
            selected_role = "user"

        user= authenticate(request, username=username,password=password)

        if user is None:
            messages.error(request, 'Wrong username or password.')
        elif selected_role == "admin" and not user.is_staff:
            messages.error(request, 'This account is not an admin account.')
        else:
            login(request ,user)
            if selected_role == "admin":
                return redirect('loan-approval-dashboard')
            return redirect('home')

    context={"selected_role": selected_role}
    return render(request, 'Authapp/login_form.html', context)

def logoutUser(request):
    context={}
    logout(request)
    return redirect('login')

def registerUser(request):
    form=UserCreationForm()
    selected_role = "user"
    if request.method=='POST':
        selected_role = request.POST.get("account_type", "user").lower()
        if selected_role not in ["user", "admin"]:
            selected_role = "user"

        form=UserCreationForm(request.POST)
        if form.is_valid():
            user=form.save(commit=False)
            user.username=user.username.lower()

            if selected_role == "admin":
                admin_code = request.POST.get("admin_code", "").strip()
                if admin_code != settings.ADMIN_REGISTRATION_CODE:
                    messages.error(request, "Invalid admin registration code.")
                    context = {"form": form, "selected_role": selected_role}
                    return render(request, 'Authapp/register_form.html', context)
                user.is_staff = True

            user.save()
            login(request,user)
            if selected_role == "admin":
                return redirect('loan-approval-dashboard')
            return redirect('home')

    context={"form": form, "selected_role": selected_role}
    return render(request, 'Authapp/register_form.html', context)

@login_required
def profile(request):
    return render(request, "Authapp/profile.html")
