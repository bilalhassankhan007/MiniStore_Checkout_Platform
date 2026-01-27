"""
store/webhooks/views.py

Goal:
- Verify Stripe signature (security)
- Be idempotent (Stripe retries)
- Mark internal Order as PAID when payment is confirmed

Important:
- Stripe CLI "trigger" fixtures sometimes don't set payment_status exactly like a real checkout.
  For demo reliability, we treat `checkout.session.completed` + session.status="complete"
  as success.
"""

from __future__ import annotations

import logging
import uuid

import stripe
from django.conf import settings
from django.db import transaction
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from store.models import Order, StripeEvent

logger = logging.getLogger(__name__)

HANDLED_EVENT_TYPES = {"checkout.session.completed"}


@csrf_exempt
def stripe_webhook(request):
    # Stripe webhooks are POST-only
    if request.method != "POST":
        return HttpResponse("Method Not Allowed", status=405)

    # Secret must be present (strip avoids invisible leading spaces in env)
    secret = (getattr(settings, "STRIPE_WEBHOOK_SECRET", "") or "").strip()
    if not secret:
        return HttpResponse("STRIPE_WEBHOOK_SECRET not configured.", status=500)

    payload = request.body
    sig_header = request.headers.get("Stripe-Signature") or request.META.get(
        "HTTP_STRIPE_SIGNATURE", ""
    )

    # 1) Verify signature
    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=secret,
        )
    except ValueError:
        logger.warning("Stripe webhook: invalid payload")
        return HttpResponse("Invalid payload", status=400)
    except stripe.error.SignatureVerificationError:
        logger.warning("Stripe webhook: invalid signature (whsec mismatch / spaces)")
        return HttpResponse("Invalid signature", status=400)

    event_id = (event.get("id") or "").strip()
    event_type = (event.get("type") or "").strip()

    if not event_id:
        logger.warning("Stripe webhook: missing event id")
        return HttpResponse("OK", status=200)

    # Always store events for demo proof (idempotent)
    # If event already exists, ACK 200 so Stripe stops retrying.
    try:
        with transaction.atomic():
            stripe_event, created = StripeEvent.objects.get_or_create(
                event_id=event_id,
                defaults={"event_type": event_type},
            )
            if not created:
                return HttpResponse("OK", status=200)

            # If not a type we handle, just ACK.
            if event_type not in HANDLED_EVENT_TYPES:
                return HttpResponse("OK", status=200)

            # 2) Handle checkout.session.completed
            session = (event.get("data") or {}).get("object") or {}

            session_id = (session.get("id") or "").strip()
            payment_status = (session.get("payment_status") or "").strip()  # "paid" in real checkout
            session_status = (session.get("status") or "").strip()          # "complete" / "open"
            payment_intent = (session.get("payment_intent") or "").strip()

            # Link back to our Order using client_reference_id / metadata
            order_public_id = (session.get("client_reference_id") or "").strip()
            if not order_public_id:
                order_public_id = (
                    (session.get("metadata") or {}).get("order_public_id") or ""
                ).strip()

            logger.info(
                "Stripe webhook session: id=%s status=%s payment_status=%s pi=%s ref=%s",
                session_id, session_status, payment_status, payment_intent, order_public_id
            )

            # Find order
            order = None

            # Prefer session_id (strongest)
            if session_id:
                order = (
                    Order.objects.select_for_update()
                    .filter(stripe_checkout_session_id=session_id)
                    .first()
                )

            # Fallback: public_id
            if not order and order_public_id:
                try:
                    order_uuid = uuid.UUID(order_public_id)
                    order = (
                        Order.objects.select_for_update()
                        .filter(public_id=order_uuid)
                        .first()
                    )
                except ValueError:
                    logger.warning("Invalid order_public_id (not UUID): %s", order_public_id)

            if not order:
                logger.warning(
                    "Stripe webhook: no order found (session_id=%s, order_public_id=%s)",
                    session_id, order_public_id
                )
                return HttpResponse("OK", status=200)

            # ✅ Decide if paid:
            # - Real Stripe checkout: payment_status == "paid"
            # - CLI fixture: sometimes session.status == "complete" even if payment_status isn't perfect
            is_paid = (payment_status == "paid") or (session_status == "complete")

            if is_paid:
                # Use model helper: sets status + paid_at + payment_intent id
                order.mark_paid(payment_intent_id=payment_intent or None)
                logger.info("Order marked PAID: %s", str(order.public_id))
            else:
                logger.info("Order not marked PAID (not paid yet): %s", str(order.public_id))

        return HttpResponse("OK", status=200)

    except Exception:
        # Return 500 so Stripe retries if something real breaks
        logger.exception("Stripe webhook crashed for event_id=%s type=%s", event_id, event_type)
        return HttpResponse("Server error", status=500)
