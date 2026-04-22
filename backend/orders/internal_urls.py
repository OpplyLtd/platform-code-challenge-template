from django.urls import path

from .internal_views import advance_status

urlpatterns = [
    path("orders/<int:pk>/advance-status/", advance_status, name="internal-advance-status"),
]
