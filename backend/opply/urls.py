from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/login/", obtain_auth_token, name="api-token-auth"),
    path("api/buyers/", include("buyers.urls")),
    path("api/suppliers/", include("suppliers.urls")),
    path("api/ingredients/", include("ingredients.urls")),
    path("api/orders/", include("orders.urls")),
    path("api/products/", include("products.urls")),
]
