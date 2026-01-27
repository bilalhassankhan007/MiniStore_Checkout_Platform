from django.contrib import admin
from store.models import Order, OrderItem, StripeEvent


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product_key", "name", "unit_amount", "quantity", "line_amount")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "public_id",
        "user",
        "status",
        "amount_total",
        "currency",
        "paid_at",
        "stripe_checkout_session_id",
        "stripe_payment_intent_id",
        "created_at",
    )
    list_filter = ("status", "currency", "created_at", "paid_at")
    search_fields = ("public_id", "user__username", "stripe_checkout_session_id", "stripe_payment_intent_id")
    readonly_fields = ("public_id", "created_at", "paid_at")
    inlines = [OrderItemInline]
    ordering = ("-id",)


@admin.register(StripeEvent)
class StripeEventAdmin(admin.ModelAdmin):
    list_display = ("id", "event_type", "event_id", "received_at")
    list_filter = ("event_type", "received_at")
    search_fields = ("event_id", "event_type")
    readonly_fields = ("event_id", "event_type", "received_at")
    ordering = ("-received_at", "-id")
