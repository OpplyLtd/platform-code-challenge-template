from django.contrib import admin
from .models import Buyer


@admin.register(Buyer)
class BuyerAdmin(admin.ModelAdmin):
    list_display = ["id", "company_name", "user", "created_at"]
    search_fields = ["company_name", "user__username", "user__email"]
