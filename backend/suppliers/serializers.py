from rest_framework import serializers
from .models import Supplier


class SupplierSerializer(serializers.ModelSerializer):
    ingredient_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Supplier
        fields = ["id", "name", "description", "created_at", "ingredient_count"]
