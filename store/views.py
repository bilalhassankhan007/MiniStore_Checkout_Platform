"""
store/views.py

Why:
- Keep UI view logic small.
- Use the canonical product catalog from store.services.products.
- Show paid orders only after webhook confirmation.
- Add a staff-only "Payments / Webhook Proof" page for hiring demo.
"""

from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import render

from store.models import Order, OrderStatus, StripeEvent
from store.services.products import PRODUCTS


def _get_products_catalog() -> list[dict]:
    """
    Convert PRODUCTS dict -> list for template rendering.

    Template expects:
      p.key, p.name, p.display_price

    Why:
    - Django templates can access dict keys via dot (p.name) cleanly.
    - Single source of truth = PRODUCTS used in serializer & checkout logic.
    """
    catalog: list[dict] = []

    for key, p in PRODUCTS.items():
        # Support both dict-style and dataclass/obj-style products (defensive).
        name = p["name"] if isinstance(p, dict) else getattr(p, "name", str(key))
        display_price = (
            p.get("display_price")
            if isinstance(p, dict)
            else getattr(p, "display_price", "")
        )

        # If display_price is missing, compute from unit_amount (cents).
        if not display_price:
            unit_amount = (
                p.get("unit_amount", 0)
                if isinstance(p, dict)
                else getattr(p, "unit_amount", 0)
            )
            display_price = f"${unit_amount / 100:.2f}"

        catalog.append({"key": key, "name": name, "display_price": display_price})

    return catalog


def home(request):
    """
    Main UI page.

    IMPORTANT:
    Template path is: store/templates/store/home.html
    So the template name must be: "store/home.html"
    """
    checkout_state = request.GET.get("checkout")

    # User-friendly feedback after Stripe redirects back.
    # Note: success means "Checkout finished", but order appears when webhook confirms.
    if checkout_state == "success":
        messages.success(
            request,
            "Payment completed. Your order will appear once webhook confirms payment.",
        )
    elif checkout_state == "cancel":
        messages.warning(request, "Checkout cancelled.")

    products = _get_products_catalog()

    orders = []
    if request.user.is_authenticated:
        orders = (
            Order.objects.filter(user=request.user, status=OrderStatus.PAID)
            .prefetch_related("items")
            .order_by("-paid_at", "-id")
        )

    return render(request, "store/home.html", {"products": products, "orders": orders})


@login_required
def webhook_status(request):
    """
    Used by the "..." dropdown in base.html.

    Returns minimal safe info for demo:
    - connected: bool
    - last event type + time (if any)
    """
    last = StripeEvent.objects.order_by("-received_at", "-id").first()
    if not last:
        return JsonResponse({"connected": False})

    return JsonResponse(
        {
            "connected": True,
            "last_event_id": last.event_id,
            "last_event_type": last.event_type,
            "received_at": last.received_at.isoformat() if last.received_at else None,
        }
    )


@staff_member_required
def debug_stripe_events(request):
    """
    Staff-only hiring demo page:
    - Shows last Stripe events (webhook proof)
    - Shows last Orders (state changes)

    Why staff_member_required:
    - Simple, secure enough for take-home demo
    - If user is not staff, they get redirected to login
    """
    events = StripeEvent.objects.order_by("-received_at", "-id")[:25]
    orders = Order.objects.select_related("user").order_by("-id")[:25]

    return render(
        request,
        "store/debug_stripe_events.html",
        {"events": events, "orders": orders},
    )
