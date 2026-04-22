from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from django.db import transaction
from ingredients.models import Ingredient
from .models import Product, ProductIngredient
from .serializers import (
    ProductSerializer,
    ProductDetailSerializer,
    ProductIngredientWriteSerializer,
)


class ProductListCreateView(ListCreateAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.filter(buyer=self.request.user.buyer_profile).prefetch_related("product_ingredients")

    def create(self, request: Request, *args, **kwargs) -> Response:
        name = request.data.get("name", "")
        description = request.data.get("description", "")
        ingredients_data = request.data.get("ingredients", [])

        if not name:
            return Response({"name": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)

        ingredient_serializer = ProductIngredientWriteSerializer(data=ingredients_data, many=True)
        ingredient_serializer.is_valid(raise_exception=True)

        buyer = request.user.buyer_profile
        with transaction.atomic():
            product = Product.objects.create(buyer=buyer, name=name, description=description)
            for item in ingredient_serializer.validated_data:
                ingredient = Ingredient.objects.get(pk=item["ingredient_id"])
                ProductIngredient.objects.create(
                    product=product,
                    ingredient=ingredient,
                    quantity=item["quantity"],
                )

        product.refresh_from_db()
        out = ProductDetailSerializer(product)
        return Response(out.data, status=status.HTTP_201_CREATED)


class ProductDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = ProductDetailSerializer

    def get_queryset(self):
        return Product.objects.filter(buyer=self.request.user.buyer_profile).prefetch_related(
            "product_ingredients__ingredient__supplier"
        )

    def update(self, request: Request, *args, **kwargs) -> Response:
        product = self.get_object()

        if "name" in request.data:
            product.name = request.data["name"]
        if "description" in request.data:
            product.description = request.data["description"]

        if "ingredients" in request.data:
            ingredient_serializer = ProductIngredientWriteSerializer(data=request.data["ingredients"], many=True)
            ingredient_serializer.is_valid(raise_exception=True)

            with transaction.atomic():
                product.save()
                product.product_ingredients.all().delete()
                for item in ingredient_serializer.validated_data:
                    ingredient = Ingredient.objects.get(pk=item["ingredient_id"])
                    ProductIngredient.objects.create(
                        product=product,
                        ingredient=ingredient,
                        quantity=item["quantity"],
                    )
        else:
            product.save()

        product.refresh_from_db()
        out = ProductDetailSerializer(product)
        return Response(out.data)
