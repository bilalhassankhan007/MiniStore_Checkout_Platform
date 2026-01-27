from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Product:
    # Why: dataclass makes catalog immutable & readable.
    key: str
    name: str
    unit_amount: int  # cents
    currency: str = "usd"

    @property
    def display_price(self) -> str:
        # Why: UI wants "$19.99" format (human friendly).
        return f"${self.unit_amount / 100:.2f}"


# Single source of truth for products.
# NOTE: Keys must match what UI sends (data-product-key) and serializer validates.
PRODUCTS: dict[str, Product] = {
    "p1": Product(key="p1", name="T-Shirt", unit_amount=1999),
    "p2": Product(key="p2", name="Hoodie", unit_amount=3999),
    "p3": Product(key="p3", name="Cap", unit_amount=1499),
}


def list_products() -> list[Product]:
    # Why: used by UI layer when we need a list.
    return list(PRODUCTS.values())


def build_order_items(quantities: dict[str, int]) -> list[dict]:
    """
    Convert quantities -> DB/service-ready order items.

    Edge cases handled:
    - qty <= 0 ignored
    - unknown product key -> ValueError (shouldn't happen if serializer validated)
    """
    items: list[dict] = []

    for product_key, qty in quantities.items():
        if not isinstance(qty, int):
            # Why: defensive programming; serializer should prevent this.
            raise ValueError(f"Invalid quantity type for {product_key}: {type(qty)}")

        if qty <= 0:
            continue

        product = PRODUCTS.get(product_key)
        if not product:
            # Why: fail fast (protects money flow).
            raise ValueError(f"Unknown product key: {product_key}")

        items.append(
            {
                "product_key": product.key,
                "name": product.name,
                "unit_amount": product.unit_amount,
                "quantity": qty,
                "line_amount": product.unit_amount * qty,
            }
        )

    return items
