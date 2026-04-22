from rest_framework import serializers
from .models import Buyer


class BuyerProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.CharField(source="user.email", read_only=True)
    total_orders = serializers.SerializerMethodField()

    class Meta:
        model = Buyer
        fields = ["id", "company_name", "username", "email", "total_orders"]

    def get_total_orders(self, obj: Buyer) -> int:
        return obj.orders.count()
