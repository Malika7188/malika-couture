from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CheckoutForm
from cart.cart import Cart
from orders.models import Address, Order, OrderItem

@login_required
def checkout(request):
    cart = Cart(request)
    items = list(cart)
    if not items:
        messages.info(request, "Your cart is empty.")
        return redirect("product_list")

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            addr = Address.objects.create(
                user=request.user,
                full_name=form.cleaned_data["full_name"],
                phone=form.cleaned_data["phone"],
                address_line1=form.cleaned_data["address_line1"],
                address_line2=form.cleaned_data["address_line2"],
                city=form.cleaned_data["city"],
                country=form.cleaned_data["country"],
            )
            order = Order.objects.create(user=request.user, shipping_address=addr, status="pending")
            for it in items:
                OrderItem.objects.create(
                    order=order,
                    product=it["product"],
                    quantity=it["quantity"],
                    unit_price=it["product"].price,
                )
            order.recalculate_total()
            for it in items:
                p = it["product"]
                p.inventory = max(0, p.inventory - it["quantity"])
                p.save()
            cart.clear()
            messages.success(request, f"Order #{order.pk} placed. Proceed to payment.")
            return redirect("orders:order_detail", pk=order.pk)
    else:
        form = CheckoutForm()

    return render(request, "checkout/checkout.html", {"form": form, "cart": cart})
