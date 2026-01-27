"""
store/webhooks/urls.py

Why:
- Keep webhook endpoints isolated (separate "concern").
- Config routes this under /stripe/
"""

from django.urls import path

from .views import stripe_webhook

urlpatterns = [
    path("webhook/", stripe_webhook, name="stripe-webhook"),
]
