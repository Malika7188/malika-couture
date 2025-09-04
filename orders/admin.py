from django.contrib import admin
from .models import Order, OrderItem, Address

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ("product","quantity","unit_price")
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id","user","status","total","created_at")
    list_filter = ("status","created_at")
    inlines = [OrderItemInline]

admin.site.register(Address)
