"""
Why: API view is a thin controller:
- parse + validate input
- call service
- return checkout url

Keep business logic in services (start_checkout).
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .serializers import CheckoutCreateSerializer
from store.services.checkout import start_checkout, CheckoutError
from store.services.stripe import StripeConfigError


class CheckoutCreateAPIView(APIView):
    """
    POST /api/checkout/
    Body:
      {
        "quantities": {"tshirt": 2, "hoodie": 1}
      }

    Returns:
      { "checkout_url": "https://checkout.stripe.com/..." }
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CheckoutCreateSerializer(
            data=request.data,
            context={"request": request},  # future-proof
        )
        serializer.is_valid(raise_exception=True)

        try:
            checkout_url = start_checkout(
                user=request.user,
                quantities=serializer.validated_data["quantities"],
                request=request,
            )
        except CheckoutError as e:
            # Bad input / cart issue / user issue (client error)
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except StripeConfigError as e:
            # Missing Stripe keys / wrong configuration (server error)
            return Response(
                {"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response({"checkout_url": checkout_url}, status=status.HTTP_200_OK)
