from django.db import models
from django.conf import settings
from decimal import Decimal

class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=30)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=120)
    country = models.CharField(max_length=120, default="Kenya")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} — {self.address_line1}, {self.city}"

class Order(models.Model):
    STATUS_CHOICES = [
        ("pending","Pending"),
        ("paid","Paid"),
        ("shipped","Shipped"),
        ("delivered","Delivered"),
        ("cancelled","Cancelled"),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    shipping_address = models.ForeignKey(Address, on_delete=models.PROTECT, related_name="orders")

    def recalculate_total(self):
        total = sum((it.quantity * it.unit_price for it in self.items.all()), Decimal("0.00"))
        self.total = total
        self.save()
        return total

    def __str__(self):
        return f"Order #{self.pk} — {self.user} — {self.status}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("products.Product", on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def line_total(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.product} × {self.quantity}"
