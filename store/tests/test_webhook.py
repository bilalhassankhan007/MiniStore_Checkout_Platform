import json
import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from store.models import Order, OrderStatus, StripeEvent


@pytest.mark.django_db
def test_webhook_marks_order_paid_and_is_idempotent(mocker, settings):
    settings.STRIPE_WEBHOOK_SECRET = "whsec_test"

    User = get_user_model()
    user = User.objects.create_user(username="u1", password="pass123")

    order = Order.objects.create(
        user=user,
        currency="usd",
        amount_total=1000,
        stripe_checkout_session_id="cs_test_1",
    )

    event = {
        "id": "evt_1",
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_test_1",
                "payment_status": "paid",
                "payment_intent": "pi_123",
            }
        },
    }

    mocker.patch("stripe.Webhook.construct_event", return_value=event)

    client = Client()
    resp1 = client.post(
        "/stripe/webhook/",
        data=json.dumps({}),
        content_type="application/json",
        HTTP_STRIPE_SIGNATURE="sig",
    )
    assert resp1.status_code == 200

    order.refresh_from_db()
    assert order.status == OrderStatus.PAID
    assert StripeEvent.objects.filter(event_id="evt_1").count() == 1

    # Duplicate webhook should not create extra StripeEvent entries or break state
    resp2 = client.post(
        "/stripe/webhook/",
        data=json.dumps({}),
        content_type="application/json",
        HTTP_STRIPE_SIGNATURE="sig",
    )
    assert resp2.status_code == 200
    assert StripeEvent.objects.filter(event_id="evt_1").count() == 1
