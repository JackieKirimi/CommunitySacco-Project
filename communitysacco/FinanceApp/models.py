from django.contrib.auth.models import User
from django.db import models


class SavingsRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="savings_records")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    notes = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} saved {self.amount}"


class LoanRequest(models.Model):
    STATUS_PENDING = "PENDING"
    STATUS_APPROVED = "APPROVED"
    STATUS_REJECTED = "REJECTED"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="loan_requests")
    name = models.CharField(max_length=120)
    id_number = models.CharField(max_length=30)
    document = models.FileField(upload_to="loan_documents/")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    purpose = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)
    admin_comment = models.CharField(max_length=255, blank=True)
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_loan_requests",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.amount} ({self.status})"


class Transaction(models.Model):
    TYPE_DEPOSIT = "DEPOSIT"
    TYPE_LOAN_DISBURSEMENT = "LOAN_DISBURSEMENT"
    TYPE_LOAN_REPAYMENT = "LOAN_REPAYMENT"
    TYPE_CHOICES = [
        (TYPE_DEPOSIT, "Deposit"),
        (TYPE_LOAN_DISBURSEMENT, "Loan Disbursement"),
        (TYPE_LOAN_REPAYMENT, "Loan Repayment"),
    ]
    STATUS_PENDING = "PENDING"
    STATUS_COMPLETED = "COMPLETED"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_COMPLETED, "Completed"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transactions")
    transaction_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_COMPLETED)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - {self.amount}"


class UserLoanLimit(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="loan_limit")
    amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} loan limit: {self.amount if self.amount is not None else 'None'}"
