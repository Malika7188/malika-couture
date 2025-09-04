from django.core.management.base import BaseCommand
from payments.models import Payment
from payments.stellar_utils import find_payment_for_memo
from django.conf import settings
from django.utils import timezone
from decimal import Decimal

class Command(BaseCommand):
    help = "Check pending Stellar payments and mark verified if found"

    def handle(self, *args, **options):
        pending = Payment.objects.filter(status="pending")
        for p in pending:
            tx_hash, amount, asset = find_payment_for_memo(settings.STELLAR_MERCHANT_PUBLIC_KEY, p.memo)
            if tx_hash:
                if asset == "XLM" and Decimal(amount) >= p.amount_xlm:
                    p.tx_hash = tx_hash
                    p.status = "verified"
                    p.verified_at = timezone.now()
                    p.save()
                    # mark order paid
                    order = p.order
                    order.status = "paid"
                    order.save()
                    self.stdout.write(self.style.SUCCESS(f"Verified payment {p.pk} tx {tx_hash}"))
                else:
                    p.status = "failed"
                    p.note = f"Tx {tx_hash} found but mismatch {amount} {asset}"
                    p.save()
                    self.stdout.write(self.style.WARNING(f"Payment {p.pk} failed: mismatch"))
            else:
                self.stdout.write(f"No tx yet for payment {p.pk}")
