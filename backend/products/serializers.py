from rest_framework import serializers
from ingredients.serializers import IngredientSerializer
from .models import Product, ProductIngredient


class ProductIngredientReadSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer(read_only=True)

    class Meta:
        model = ProductIngredient
        fields = ["ingredient", "quantity"]


class ProductIngredientWriteSerializer(serializers.Serializer):
    ingredient_id = serializers.IntegerField()
    quantity = serializers.DecimalField(max_digits=10, decimal_places=3, min_value="0.001")


class ProductSerializer(serializers.ModelSerializer):
    ingredient_count = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ["id", "name", "description", "ingredient_count", "created_at"]

    def get_ingredient_count(self, obj: Product) -> int:
        return obj.product_ingredients.count()


class ProductDetailSerializer(ProductSerializer):
    ingredients = ProductIngredientReadSerializer(source="product_ingredients", many=True, read_only=True)

    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + ["ingredients", "updated_at"]
