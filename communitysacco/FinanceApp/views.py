from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import LoanRequestForm, SavingsRecordForm
from .models import LoanRequest, Transaction, UserLoanLimit
from django.http import HttpResponse
from django_daraja.mpesa.core import MpesaClient

def index(request):
    cl = MpesaClient()
    # Use a Safaricom phone number that you have access to, for you to be able to view the prompt.
    phone_number = '+254742252718'
    amount = 1
    account_reference = 'reference'
    transaction_desc = 'Description'
    callback_url = 'https://api.darajambili.com/express-payment'
    response = cl.stk_push(phone_number, amount, account_reference, transaction_desc, callback_url)
    return HttpResponse(response)



def _is_staff(user):
    return user.is_authenticated and user.is_staff


@login_required
def savings(request):
    if request.method == "POST":
        form = SavingsRecordForm(request.POST)
        if form.is_valid():
            savings_record = form.save(commit=False)
            savings_record.user = request.user
            savings_record.save()
            Transaction.objects.create(
                user=request.user,
                transaction_type=Transaction.TYPE_DEPOSIT,
                status=Transaction.STATUS_COMPLETED,
                amount=savings_record.amount,
                description=savings_record.notes or "Savings deposit",
            )
            messages.success(request, "Savings record added successfully.")
            return redirect("savings")
    else:
        form = SavingsRecordForm()

    records = request.user.savings_records.all()
    total_saved = records.aggregate(total=Sum("amount"))["total"] or 0
    context = {"form": form, "records": records, "total_saved": total_saved}
    return render(request, "FinanceApp/savings.html", context)


@login_required
def loans(request):
    if request.method == "POST":
        form = LoanRequestForm(request.POST, request.FILES)
        if form.is_valid():
            loan_request = form.save(commit=False)
            loan_request.user = request.user
            loan_request.save()
            messages.success(request, "Loan request submitted and awaiting admin approval.")
            return redirect("loans")
    else:
        form = LoanRequestForm(initial={"name": request.user.get_full_name() or request.user.username})

    user_loans = request.user.loan_requests.all()
    context = {"form": form, "loan_requests": user_loans}
    return render(request, "FinanceApp/loans.html", context)


@login_required
def transactions(request):
    user_transactions = request.user.transactions.all()
    return render(request, "FinanceApp/transactions.html", {"transactions": user_transactions})


def admin_login(request):
    return redirect("/Authapp/login/?role=admin")


@login_required(login_url="admin-login")
@user_passes_test(_is_staff, login_url="admin-login")
def loan_approval_dashboard(request):
    if request.method == "POST":
        action = request.POST.get("action")

        if action in [LoanRequest.STATUS_APPROVED, LoanRequest.STATUS_REJECTED]:
            loan_request = get_object_or_404(LoanRequest, id=request.POST.get("loan_id"))
            admin_comment = request.POST.get("admin_comment", "").strip()
            if loan_request.user_id == request.user.id:
                messages.error(request, "You cannot approve or reject your own loan request.")
                return redirect("loan-approval-dashboard")
            loan_request.status = action
            loan_request.admin_comment = admin_comment
            loan_request.reviewed_by = request.user
            loan_request.reviewed_at = timezone.now()
            loan_request.save()

            if action == LoanRequest.STATUS_APPROVED:
                Transaction.objects.create(
                    user=loan_request.user,
                    transaction_type=Transaction.TYPE_LOAN_DISBURSEMENT,
                    status=Transaction.STATUS_COMPLETED,
                    amount=loan_request.amount,
                    description=f"Approved loan: {loan_request.name}",
                )
                messages.success(request, "Loan approved successfully.")
            else:
                messages.info(request, "Loan rejected.")
        elif action == "SET_LIMIT":
            target_user_id = request.POST.get("target_user_id")
            raw_limit = request.POST.get("loan_limit_amount", "").strip()
            target_user = get_object_or_404(User, id=target_user_id)
            loan_limit_obj, _ = UserLoanLimit.objects.get_or_create(user=target_user)
            if raw_limit:
                try:
                    loan_limit_obj.amount = Decimal(raw_limit)
                except InvalidOperation:
                    messages.error(request, "Invalid loan limit amount.")
                    return redirect("loan-approval-dashboard")
            else:
                loan_limit_obj.amount = None
            loan_limit_obj.save()
            messages.success(request, f"Loan limit updated for {target_user.username}.")
        return redirect("loan-approval-dashboard")

    pending_loans = LoanRequest.objects.filter(status=LoanRequest.STATUS_PENDING)
    all_loans = LoanRequest.objects.select_related("user", "reviewed_by")
    applicants = User.objects.filter(loan_requests__isnull=False).distinct().order_by("username")
    limits_by_user_id = {limit.user_id: limit.amount for limit in UserLoanLimit.objects.filter(user__in=applicants)}
    applicants_with_limits = [
        {"id": applicant.id, "username": applicant.username, "limit": limits_by_user_id.get(applicant.id)}
        for applicant in applicants
    ]
    context = {
        "pending_loans": pending_loans,
        "all_loans": all_loans,
        "applicants_with_limits": applicants_with_limits,
    }
    return render(request, "FinanceApp/loan_approval_dashboard.html", context)

def mpesaPayment(request):
    if request.method == "POST":
        phone_number = request.POST.get("phonenumber")
        amount = int(float(request.POST.get("amount")))
        cl = MpesaClient()
    # Use a Safaricom phone number that you have access to, for you to be able to view the prompt.
        phone_number = phone_number
        amount = amount
        account_reference = 'FinanceApp Payment'
        transaction_desc = 'savings deposit'
        callback_url = 'https://api.darajambili.com/express-payment'
        response = cl.stk_push(phone_number, amount, account_reference, transaction_desc, callback_url)
    else:
        pass   
    context = {}
    return render(request, 'FinanceApp/prompt_stk_push.html', context)