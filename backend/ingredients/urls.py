from django.urls import path
from .views import IngredientListView

urlpatterns = [
    path("", IngredientListView.as_view(), name="ingredient-list"),
]
