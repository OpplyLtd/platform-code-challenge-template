from django.contrib import admin
from .models import Product, ProductIngredient


class ProductIngredientInline(admin.TabularInline):
    model = ProductIngredient
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "buyer", "created_at", "updated_at"]
    list_filter = ["buyer"]
    search_fields = ["name", "buyer__company_name", "buyer__user__username"]
    inlines = [ProductIngredientInline]


@admin.register(ProductIngredient)
class ProductIngredientAdmin(admin.ModelAdmin):
    list_display = ["id", "product", "ingredient", "quantity"]
    search_fields = ["product__name", "ingredient__name"]
