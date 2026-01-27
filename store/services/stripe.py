# Why: Stripe calls should be isolated behind a small wrapper.
# - Easier to mock in tests
# - Keeps business logic clean
# - Keeps Stripe config in one place

from __future__ import annotations

import stripe
from django.conf import settings


class StripeConfigError(RuntimeError):
    pass


def _configure() -> None:
    """
    Configure Stripe client.
    We strip() keys to avoid hidden leading spaces (common .env mistake).
    """
    secret = (getattr(settings, "STRIPE_SECRET_KEY", "") or "").strip()
    if not secret:
        raise StripeConfigError("STRIPE_SECRET_KEY is missing in environment (.env).")

    stripe.api_key = secret


def create_checkout_session(
    *,
    order_public_id: str,
    currency: str,
    items: list[dict],
    success_url: str,
    cancel_url: str,
    customer_email: str | None = None,
):
    """
    Create a Stripe Checkout Session.

    IMPORTANT:
    - Don't pass "timeout" into Session.create(). Stripe will treat it as an API param and fail.
    - Idempotency key prevents duplicate sessions if request retries.
    """
    _configure()

    idempotency_key = f"checkout_{order_public_id}"

    line_items = [
        {
            "price_data": {
                "currency": currency,
                "product_data": {"name": i["name"]},
                "unit_amount": int(i["unit_amount"]),
            },
            "quantity": int(i["quantity"]),
        }
        for i in items
    ]

    payload = {
        "mode": "payment",
        "line_items": line_items,
        "success_url": success_url,
        "cancel_url": cancel_url,
        "client_reference_id": order_public_id,
        "metadata": {"order_public_id": order_public_id},
    }

    # Optional (nice for Stripe dashboard)
    if customer_email:
        payload["customer_email"] = customer_email

    # idempotency_key is OK here (Stripe python treats it as request option/header)
    return stripe.checkout.Session.create(**payload, idempotency_key=idempotency_key)
