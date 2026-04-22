from decimal import Decimal
from rest_framework import serializers
from ingredients.serializers import IngredientSerializer
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer(read_only=True)
    line_total = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ["ingredient", "quantity", "unit_price", "line_total"]

    def get_line_total(self, obj: OrderItem) -> str:
        return str(Decimal(str(obj.unit_price)) * obj.quantity)


class OrderItemCreateSerializer(serializers.Serializer):
    ingredient_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class OrderSerializer(serializers.ModelSerializer):
    item_count = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ["id", "status", "created_at", "item_count", "total_amount"]

    def get_item_count(self, obj: Order) -> int:
        return obj.items.count()

    def get_total_amount(self, obj: Order) -> str:
        total = sum(
            Decimal(str(item.unit_price)) * item.quantity
            for item in obj.items.all()
        )
        return str(total)


class OrderDetailSerializer(OrderSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta(OrderSerializer.Meta):
        fields = OrderSerializer.Meta.fields + ["items", "updated_at"]


class OrderCreateSerializer(serializers.Serializer):
    items = OrderItemCreateSerializer(many=True)
