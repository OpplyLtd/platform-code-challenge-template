from django.db.models import Count
from rest_framework.generics import ListAPIView, RetrieveAPIView
from .models import Supplier
from .serializers import SupplierSerializer
from ingredients.serializers import IngredientSerializer


class SupplierListView(ListAPIView):
    serializer_class = SupplierSerializer

    def get_queryset(self):
        return Supplier.objects.annotate(ingredient_count=Count("ingredients"))


class SupplierDetailView(RetrieveAPIView):
    serializer_class = SupplierSerializer

    def get_queryset(self):
        return Supplier.objects.annotate(ingredient_count=Count("ingredients"))


class SupplierIngredientListView(ListAPIView):
    serializer_class = IngredientSerializer

    def get_queryset(self):
        from ingredients.models import Ingredient
        return Ingredient.objects.filter(supplier_id=self.kwargs["pk"])
