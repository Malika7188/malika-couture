# payments/models.py
from django.db import models
from django.utils import timezone
import secrets

class Payment(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("verified", "Verified"),
        ("failed", "Failed"),
    ]

    order = models.ForeignKey("orders.Order", on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=12, decimal_places=2)        # store currency amount, e.g., KES
    amount_xlm = models.DecimalField(max_digits=18, decimal_places=7)   # required XLM amount
    currency = models.CharField(max_length=8, default="KES")
    memo = models.CharField(max_length=28, unique=True, blank=True)     # 28 bytes max
    tx_hash = models.CharField(max_length=128, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Payment {self.pk} for Order #{self.order.pk} ({self.status})"

    def save(self, *args, **kwargs):
        # ensure memo exists (safe for migrations)
        if not self.memo:
            # token_hex(12) => 24 hex chars => safe under 28-byte memo text limit
            self.memo = secrets.token_hex(12)
        super().save(*args, **kwargs)
