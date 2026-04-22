from django.db import models
from suppliers.models import Supplier


class Ingredient(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="ingredients")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    unit = models.CharField(max_length=50)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.supplier.name})"
