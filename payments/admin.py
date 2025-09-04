from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id","order","amount","amount_xlm","currency","status","memo","tx_hash","created_at")
    list_filter = ("status","currency")
    search_fields = ("memo","tx_hash","order__id","order__user__username")
