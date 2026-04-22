from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["unit_price"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "buyer", "status", "created_at", "updated_at"]
    list_filter = ["status"]
    search_fields = ["buyer__company_name", "buyer__user__username"]
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["id", "order", "ingredient", "quantity", "unit_price"]
    search_fields = ["ingredient__name", "order__buyer__company_name"]
