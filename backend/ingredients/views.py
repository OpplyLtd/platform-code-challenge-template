from rest_framework.generics import ListAPIView
from .models import Ingredient
from .serializers import IngredientSerializer


class IngredientListView(ListAPIView):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.select_related("supplier").all()
