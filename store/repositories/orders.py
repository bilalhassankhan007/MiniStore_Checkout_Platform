# Why repository:
# - Keeps ORM usage in one place
# - Services operate with clear intent: create order, attach session, etc.

from __future__ import annotations

from django.db import transaction
from store.models import Order, OrderItem


@transaction.atomic
def create_order_with_items(*, user, currency: str, items: list[dict]) -> Order:
    """
    Create an Order + OrderItems atomically.

    Edge cases:
    - items empty -> raise early (caller bug)
    - line_amount missing -> KeyError (caller bug)
    """
    if not items:
        raise ValueError("create_order_with_items: items cannot be empty")

    total = sum(int(i["line_amount"]) for i in items)

    order = Order.objects.create(
        user=user,
        currency=currency,
        amount_total=total,
    )

    OrderItem.objects.bulk_create(
        [
            OrderItem(
                order=order,
                product_key=i["product_key"],
                name=i["name"],
                unit_amount=int(i["unit_amount"]),
                quantity=int(i["quantity"]),
                line_amount=int(i["line_amount"]),
            )
            for i in items
        ]
    )

    return order


def set_checkout_session(order: Order, *, session_id: str) -> None:
    """
    Attach Stripe session id to the order.

    Why:
    - Keep write minimal (single UPDATE)
    - Avoid extra select/re-save side effects
    """
    Order.objects.filter(pk=order.pk).update(stripe_checkout_session_id=session_id)
    order.stripe_checkout_session_id = session_id  # Keep in-memory object consistent


def find_order_by_session_id(session_id: str) -> Order | None:
    """
    Non-locking lookup (useful outside webhooks).
    """
    if not session_id:
        return None
    return Order.objects.filter(stripe_checkout_session_id=session_id).first()


def lock_order_by_session_id(session_id: str) -> Order | None:
    """
    Locking lookup for webhook processing.
    MUST be called inside transaction.atomic().

    Why:
    - Avoid race conditions if Stripe retries fast.
    """
    if not session_id:
        return None
    return (
        Order.objects.select_for_update()
        .filter(stripe_checkout_session_id=session_id)
        .first()
    )
