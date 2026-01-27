import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_checkout_requires_auth():
    c = APIClient()
    resp = c.post("/api/checkout/", {"quantities": {"p1": 1}}, format="json")
    assert resp.status_code in (401, 403)


@pytest.mark.django_db
def test_checkout_returns_checkout_url(mocker):
    # Mock Stripe create call to avoid hitting network
    mock_session = type(
        "S", (), {"id": "cs_test_123", "url": "https://stripe.test/checkout"}
    )()
    mocker.patch(
        "store.services.stripe.create_checkout_session", return_value=mock_session
    )

    User = get_user_model()
    user = User.objects.create_user(username="u1", password="pass123")

    c = APIClient()
    c.login(username="u1", password="pass123")

    resp = c.post(
        "/api/checkout/", {"quantities": {"p1": 1, "p2": 0, "p3": 0}}, format="json"
    )
    assert resp.status_code == 200
    assert "checkout_url" in resp.data
