"""
store/urls.py

Why:
- Keep app routing in the app.
- Home view name "home" is used by checkout service (reverse("home")).
- webhook-status name is used by base.html dropdown.
- debug-stripe-events is a staff-only hiring demo page.
"""

from django.urls import path
from .views import home, webhook_status, debug_stripe_events

urlpatterns = [
    path("", home, name="home"),
    path("webhook-status/", webhook_status, name="webhook-status"),
    path("debug/stripe-events/", debug_stripe_events, name="debug-stripe-events"),
]
