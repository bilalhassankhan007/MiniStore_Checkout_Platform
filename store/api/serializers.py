"""
Why: Validation belongs here (not in the view).
DRF serializer ensures consistent error messages + guards against bad inputs.
"""

from rest_framework import serializers
from store.services.products import PRODUCTS


class CheckoutCreateSerializer(serializers.Serializer):
    """
    quantities: Map of product_key -> quantity
    Example:
      { "tshirt": 2, "hoodie": 1 }
    """

    quantities = serializers.DictField(
        child=serializers.IntegerField(min_value=0),
        allow_empty=False,
        help_text="Map of product_key -> quantity",
    )

    def validate_quantities(self, value: dict) -> dict:
        # Extra guard: some clients still send {} or null-ish payloads
        if not value:
            raise serializers.ValidationError("Quantities cannot be empty.")

        # PRODUCTS must be a dict like: {"tshirt": {...}, "hoodie": {...}}
        invalid = [k for k in value.keys() if k not in PRODUCTS]
        if invalid:
            raise serializers.ValidationError(f"Invalid product keys: {invalid}")

        # Guard: prevent unrealistic quantities / abuse
        for k, qty in value.items():
            if qty > 99:
                raise serializers.ValidationError(
                    f"Quantity too large for {k}. Max 99 allowed."
                )

        # Guard: prevent all zero cart
        if all(qty == 0 for qty in value.values()):
            raise serializers.ValidationError(
                "At least one item must have quantity > 0."
            )

        return value
