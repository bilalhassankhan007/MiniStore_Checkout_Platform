from django.urls import path
from .views import CheckoutCreateAPIView

urlpatterns = [
    path("checkout/", CheckoutCreateAPIView.as_view(), name="api-checkout"),
]
