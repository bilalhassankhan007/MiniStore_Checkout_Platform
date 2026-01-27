from __future__ import annotations

from django.urls import reverse

from store.repositories.orders import create_order_with_items, set_checkout_session
from store.services.products import build_order_items
from store.services import stripe as stripe_service


class CheckoutError(RuntimeError):
    pass


def start_checkout(*, user, quantities: dict[str, int], request) -> str:
    items = build_order_items(quantities)
    if not items:
        raise CheckoutError("Please add at least one item (quantity > 0).")

    currency = "usd"

    order = create_order_with_items(user=user, currency=currency, items=items)

    success_url = request.build_absolute_uri(reverse("home")) + "?checkout=success"
    cancel_url = request.build_absolute_uri(reverse("home")) + "?checkout=cancel"

    try:
        session = stripe_service.create_checkout_session(
            order_public_id=str(order.public_id),
            currency=currency,
            items=items,
            success_url=success_url,
            cancel_url=cancel_url,
            customer_email=(getattr(user, "email", "") or None),
        )
    except Exception:
        # Avoid dangling orders if Stripe session creation fails
        order.mark_failed()
        raise

    set_checkout_session(order, session_id=session.id)
    return session.url
