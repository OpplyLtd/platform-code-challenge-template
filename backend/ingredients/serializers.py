from rest_framework import serializers
from .models import Ingredient


class IngredientSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source="supplier.name", read_only=True)

    class Meta:
        model = Ingredient
        fields = ["id", "supplier_id", "supplier_name", "name", "description", "unit", "price_per_unit"]
