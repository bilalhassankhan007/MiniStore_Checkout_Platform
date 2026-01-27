# Why: central route map. We keep it thin and delegate by concern:
# - UI: store.urls
# - API: store.api.urls
# - Webhook: store.webhooks.urls
# - Auth: django.contrib.auth.urls

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    # Built-in auth endpoints:
    # /accounts/login/ , /accounts/logout/ etc.
    path("accounts/", include("django.contrib.auth.urls")),
    # UI
    path("", include("store.urls")),
    # DRF API
    path("api/", include("store.api.urls")),
    # Stripe webhooks
    path("stripe/", include("store.webhooks.urls")),
]
