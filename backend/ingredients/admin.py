from django.contrib import admin
from .models import Ingredient


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "supplier", "unit", "price_per_unit"]
    search_fields = ["name", "supplier__name"]
    list_filter = ["supplier"]
