# Why these models:
# - Order/OrderItem represent our internal source of truth for purchases.
# - StripeEvent stores webhook event IDs so webhook handling is idempotent.
#   Stripe can retry events; we must safely ignore duplicates.

from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class OrderStatus(models.TextChoices):
    CREATED = "created", "Created"
    PAID = "paid", "Paid"
    FAILED = "failed", "Failed"


class Order(models.Model):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
    )

    status = models.CharField(
        max_length=16,
        choices=OrderStatus.choices,
        default=OrderStatus.CREATED,
    )

    currency = models.CharField(max_length=8, default="usd")
    amount_total = models.PositiveIntegerField(default=0)  # cents

    stripe_checkout_session_id = models.CharField(
        max_length=255, blank=True, null=True, unique=True
    )
    stripe_payment_intent_id = models.CharField(
        max_length=255, blank=True, null=True, unique=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(blank=True, null=True)

    def mark_paid(self, payment_intent_id: str | None = None) -> None:
        """
        Mark order as paid.

        Idempotent:
        - Stripe may send the same webhook multiple times.
        - We may already be PAID, but still want to fill missing fields safely.
        """
        update_fields: list[str] = []
        now = timezone.now()

        # If not already PAID, transition + set paid_at
        if self.status != OrderStatus.PAID:
            self.status = OrderStatus.PAID
            update_fields.append("status")

            # Set paid_at once
            if not self.paid_at:
                self.paid_at = now
                update_fields.append("paid_at")

        # Even if already PAID, we can safely set payment_intent if missing/different
        if payment_intent_id:
            if self.stripe_payment_intent_id != payment_intent_id:
                self.stripe_payment_intent_id = payment_intent_id
                update_fields.append("stripe_payment_intent_id")

        if update_fields:
            # remove duplicates if any
            update_fields = list(dict.fromkeys(update_fields))
            self.save(update_fields=update_fields)

    def mark_failed(self) -> None:
        # Why: if Stripe session creation fails, we don’t want “dangling” created orders.
        if self.status != OrderStatus.PAID:
            self.status = OrderStatus.FAILED
            self.save(update_fields=["status"])

    @property
    def amount_display(self) -> str:
        return f"{self.amount_total / 100:.2f} {self.currency.upper()}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")

    product_key = models.CharField(max_length=64)
    name = models.CharField(max_length=255)

    unit_amount = models.PositiveIntegerField()  # cents
    quantity = models.PositiveIntegerField()
    line_amount = models.PositiveIntegerField()  # cents

    def __str__(self) -> str:
        return f"{self.name} x {self.quantity}"


class StripeEvent(models.Model):
    # Why: webhook idempotency. Unique event_id ensures duplicates are ignored.
    event_id = models.CharField(max_length=255, unique=True)
    event_type = models.CharField(max_length=255)
    received_at = models.DateTimeField(auto_now_add=True)
