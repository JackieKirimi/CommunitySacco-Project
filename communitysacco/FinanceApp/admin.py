from django.contrib import admin

from .models import LoanRequest, SavingsRecord, Transaction, UserLoanLimit


@admin.register(SavingsRecord)
class SavingsRecordAdmin(admin.ModelAdmin):
    list_display = ("user", "amount", "created_at")
    search_fields = ("user__username",)


@admin.register(LoanRequest)
class LoanRequestAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "id_number", "amount", "status", "created_at")
    search_fields = ("name", "user__username", "id_number")
    list_filter = ("status", "created_at")


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("user", "transaction_type", "status", "amount", "created_at")
    search_fields = ("user__username", "description")
    list_filter = ("transaction_type", "status", "created_at")


@admin.register(UserLoanLimit)
class UserLoanLimitAdmin(admin.ModelAdmin):
    list_display = ("user", "amount", "updated_at")
    search_fields = ("user__username",)
