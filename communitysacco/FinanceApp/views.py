import json
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .forms import LoanRequestForm, SavingsRecordForm
from .models import LoanRequest, Transaction, UserLoanLimit
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
            messages.success(request, "Savings record added. You can pay now or later using the Pay button in history.")
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


@login_required
def mpesaPayment(request):
    initial_payment_type = request.GET.get("payment_type", Transaction.TYPE_DEPOSIT)
    initial_amount = request.GET.get("amount", "")
    if initial_payment_type not in [Transaction.TYPE_DEPOSIT, Transaction.TYPE_LOAN_REPAYMENT]:
        initial_payment_type = Transaction.TYPE_DEPOSIT

    if request.method == "POST":
        phone_number = request.POST.get("phonenumber", "").strip()
        payment_type = request.POST.get("payment_type", Transaction.TYPE_DEPOSIT)
        raw_amount = request.POST.get("amount", "").strip()

        if payment_type not in [Transaction.TYPE_DEPOSIT, Transaction.TYPE_LOAN_REPAYMENT]:
            payment_type = Transaction.TYPE_DEPOSIT

        try:
            amount_decimal = Decimal(raw_amount)
            if amount_decimal <= 0:
                raise InvalidOperation
        except (InvalidOperation, TypeError):
            messages.error(request, "Enter a valid payment amount greater than zero.")
            return render(
                request,
                "FinanceApp/prompt_stk_push.html",
                {"initial_payment_type": payment_type, "initial_amount": raw_amount, "initial_phone_number": phone_number},
            )

        if not phone_number:
            messages.error(request, "Phone number is required.")
            return render(
                request,
                "FinanceApp/prompt_stk_push.html",
                {"initial_payment_type": payment_type, "initial_amount": raw_amount, "initial_phone_number": phone_number},
            )

        cl = MpesaClient()
        callback_url = _resolve_callback_url(request)
        account_reference = "FinanceApp"
        transaction_desc = "Loan repay" if payment_type == Transaction.TYPE_LOAN_REPAYMENT else "Savings"

        try:
            response = cl.stk_push(
                phone_number,
                int(amount_decimal),
                account_reference,
                transaction_desc,
                callback_url,
            )
            response_code = str(getattr(response, "response_code", "") or "")
            response_desc = getattr(response, "response_description", "") or ""
            error_message = getattr(response, "error_message", "") or ""
            customer_message = getattr(response, "customer_message", "") or ""

            if response_code != "0":
                problem_text = error_message or response_desc or customer_message or "STK request was not accepted."
                messages.error(request, f"STK push failed: {problem_text}")
                return render(
                    request,
                    "FinanceApp/prompt_stk_push.html",
                    {"initial_payment_type": payment_type, "initial_amount": raw_amount, "initial_phone_number": phone_number},
                )

            payment_reference = _extract_checkout_id(response)
            Transaction.objects.create(
                user=request.user,
                transaction_type=payment_type,
                status=Transaction.STATUS_PENDING,
                amount=amount_decimal,
                phone_number=phone_number,
                payment_reference=payment_reference,
                description=f"STK push initiated for {transaction_desc.lower()}",
            )
            messages.success(
                request,
                "STK push sent. Check your phone to complete payment. Status will remain Pending payment until confirmed.",
            )
        except Exception:
            messages.error(request, "Unable to initiate STK push. Please retry.")

    context = {
        "initial_payment_type": initial_payment_type,
        "initial_amount": initial_amount,
    }
    return render(request, "FinanceApp/prompt_stk_push.html", context)


def _extract_checkout_id(response):
    if isinstance(response, dict):
        return (
            response.get("CheckoutRequestID")
            or response.get("checkout_request_id")
            or response.get("checkoutRequestID")
            or ""
        )

    checkout_from_attr = getattr(response, "checkout_request_id", None)
    if checkout_from_attr:
        return str(checkout_from_attr)

    response_data = getattr(response, "response", None)
    if isinstance(response_data, dict):
        return str(
            response_data.get("CheckoutRequestID")
            or response_data.get("checkout_request_id")
            or response_data.get("checkoutRequestID")
            or ""
        )

    return ""


def _resolve_callback_url(request):
    configured_callback = getattr(settings, "MPESA_CALLBACK_URL", "").strip()
    if configured_callback:
        return configured_callback

    auto_callback = request.build_absolute_uri(reverse("mpesa-callback"))
    if auto_callback.startswith("https://") and "localhost" not in auto_callback and "127.0.0.1" not in auto_callback:
        return auto_callback

    # Public fallback used in local development; replace with your deployed callback endpoint.
    return "https://api.darajambili.com/express-payment"


@csrf_exempt
def mpesa_callback(request):
    if request.method != "POST":
        return JsonResponse({"ResultCode": 1, "ResultDesc": "Invalid request method"}, status=405)

    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        payload = {}

    callback_data = payload.get("Body", {}).get("stkCallback", {})
    checkout_request_id = callback_data.get("CheckoutRequestID") or payload.get("CheckoutRequestID")
    result_code = callback_data.get("ResultCode", payload.get("ResultCode"))

    if checkout_request_id:
        transaction = Transaction.objects.filter(payment_reference=checkout_request_id).order_by("-created_at").first()
        if transaction:
            transaction.status = (
                Transaction.STATUS_COMPLETED if str(result_code) == "0" else Transaction.STATUS_PENDING
            )
            if str(result_code) != "0":
                transaction.description = (
                    f"{transaction.description}. Payment not completed yet."
                    if transaction.description
                    else "Payment not completed yet."
                )
            transaction.save(update_fields=["status", "description"])

    return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})


@login_required(login_url="admin-login")
@user_passes_test(_is_staff, login_url="admin-login")
def admin_analytics_dashboard(request):
    loan_status_counts = LoanRequest.objects.values("status").annotate(total=Count("id")).order_by("status")
    loan_status_labels = [item["status"].title() for item in loan_status_counts]
    loan_status_data = [item["total"] for item in loan_status_counts]

    repayment_status_counts = (
        Transaction.objects.filter(transaction_type=Transaction.TYPE_LOAN_REPAYMENT)
        .values("status")
        .annotate(total=Count("id"))
        .order_by("status")
    )
    repayment_status_labels = ["Completed" if item["status"] == Transaction.STATUS_COMPLETED else "Pending payment" for item in repayment_status_counts]
    repayment_status_data = [item["total"] for item in repayment_status_counts]

    monthly_transactions = (
        Transaction.objects.annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(total=Count("id"))
        .order_by("month")
    )
    monthly_labels = [item["month"].strftime("%b %Y") for item in monthly_transactions if item["month"]]
    monthly_data = [item["total"] for item in monthly_transactions if item["month"]]

    recent_payment_transactions = (
        Transaction.objects.filter(
            transaction_type__in=[Transaction.TYPE_DEPOSIT, Transaction.TYPE_LOAN_REPAYMENT]
        )
        .select_related("user")
        .order_by("-created_at")[:15]
    )

    total_applicants = LoanRequest.objects.values("user_id").distinct().count()
    total_loan_repayment = (
        Transaction.objects.filter(
            transaction_type=Transaction.TYPE_LOAN_REPAYMENT,
            status=Transaction.STATUS_COMPLETED,
        ).aggregate(total=Sum("amount"))["total"]
        or 0
    )
    pending_payments = Transaction.objects.filter(status=Transaction.STATUS_PENDING).count()

    context = {
        "total_applicants": total_applicants,
        "total_loan_requests": LoanRequest.objects.count(),
        "approved_loans": LoanRequest.objects.filter(status=LoanRequest.STATUS_APPROVED).count(),
        "pending_payments": pending_payments,
        "total_loan_repayment": total_loan_repayment,
        "recent_payment_transactions": recent_payment_transactions,
        "loan_status_labels": json.dumps(loan_status_labels),
        "loan_status_data": json.dumps(loan_status_data),
        "repayment_status_labels": json.dumps(repayment_status_labels),
        "repayment_status_data": json.dumps(repayment_status_data),
        "monthly_labels": json.dumps(monthly_labels),
        "monthly_data": json.dumps(monthly_data),
    }
    return render(request, "FinanceApp/admin_analytics_dashboard.html", context)
