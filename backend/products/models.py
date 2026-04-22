from django.db import models
from buyers.models import Buyer
from ingredients.models import Ingredient


class Product(models.Model):
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.buyer})"


class ProductIngredient(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_ingredients")
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT, related_name="product_ingredients")
    quantity = models.DecimalField(max_digits=10, decimal_places=3)

    class Meta:
        unique_together = [("product", "ingredient")]

    def __str__(self) -> str:
        return f"{self.quantity} x {self.ingredient.name} in {self.product.name}"
