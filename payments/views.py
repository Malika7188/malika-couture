# from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.utils import timezone
from decimal import Decimal, ROUND_DOWN
from .models import Payment
from .stellar_utils import find_payment_for_memo
from orders.models import Order
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def _to_xlm(amount_decimal):
    """Convert store currency (KES) amount to XLM using settings.KES_PER_XLM."""
    if settings.PRICE_CURRENCY == "KES":
        xlm = (Decimal(amount_decimal) / settings.KES_PER_XLM).quantize(Decimal("0.0000001"), rounding=ROUND_DOWN)
        return xlm
    return Decimal(amount_decimal).quantize(Decimal("0.0000001"), rounding=ROUND_DOWN)

@login_required
def initiate_payment(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    # If order is already paid, redirect
    if order.status == "paid":
        messages.info(request, "Order already paid.")
        return redirect("orders:order_detail", pk=order.pk)

    # If payment exists and still pending, reuse; otherwise create new
    pending = order.payments.filter(status="pending").order_by("-created_at").first()
    if pending:
        payment = pending
    else:
        amount_kes = order.total
        amount_xlm = _to_xlm(amount_kes)
        payment = Payment.objects.create(
            order=order,
            amount=amount_kes,
            amount_xlm=amount_xlm,
            currency=settings.PRICE_CURRENCY,
        )

    context = {
        "order": order,
        "payment": payment,
        "merchant_pub": settings.STELLAR_MERCHANT_PUBLIC_KEY,
        "horizon": settings.STELLAR_HORIZON_URL,
    }
    return render(request, "payments/initiate.html", context)

@login_required
def verify_payment(request, payment_id):
    payment = get_object_or_404(Payment, pk=payment_id, order__user=request.user)
    if payment.status == "verified":
        messages.success(request, "Payment already verified.")
        return redirect("orders:order_detail", pk=payment.order.pk)

    tx_hash, amount, asset = find_payment_for_memo(settings.STELLAR_MERCHANT_PUBLIC_KEY, payment.memo)
    if tx_hash:
        # Accept if native XLM and amount >= required
        if asset == "XLM" and amount >= payment.amount_xlm:
            payment.tx_hash = tx_hash
            payment.status = "verified"
            payment.verified_at = timezone.now()
            payment.save()
            payment.order.status = "paid"
            payment.order.save()
            messages.success(request, f"Payment verified on-chain (tx {tx_hash}). Thank you!")
            return redirect("orders:order_detail", pk=payment.order.pk)
        else:
            payment.status = "failed"
            payment.note = f"Found tx {tx_hash} but asset/amount mismatch: {amount} {asset}"
            payment.tx_hash = tx_hash
            payment.save()
            messages.error(request, "Payment found but asset/amount mismatch. See payment note in admin.")
            return redirect("payments:initiate_payment", order_id=payment.order.pk)
    else:
        messages.info(request, "No matching transaction found yet. Try again after a moment.")
        return redirect("payments:initiate_payment", order_id=payment.order.pk)
