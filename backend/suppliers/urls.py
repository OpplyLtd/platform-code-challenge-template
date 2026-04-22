from django.urls import path
from .views import SupplierListView, SupplierDetailView, SupplierIngredientListView

urlpatterns = [
    path("", SupplierListView.as_view(), name="supplier-list"),
    path("<int:pk>/", SupplierDetailView.as_view(), name="supplier-detail"),
    path("<int:pk>/ingredients/", SupplierIngredientListView.as_view(), name="supplier-ingredients"),
]
