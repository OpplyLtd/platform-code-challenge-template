from django.urls import path
from .views import BuyerProfileView

urlpatterns = [
    path("me/", BuyerProfileView.as_view(), name="buyer-profile"),
]
