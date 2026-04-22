"""Internal API for advancing order state from platform-side services.

Exposed at `/api/internal/orders/<id>/advance-status/`. Intended for
internal callers only — authenticated via a shared secret header
(`X-Internal-Secret`). Suitable targets: Lambdas, worker services,
anything that owns part of the order fulfilment flow.

The endpoint is idempotent for no-op calls (requesting the current
status returns 200 with the order). Invalid transitions return 409.
"""
from django.conf import settings
from rest_framework import status as http_status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Order
from .serializers import OrderDetailSerializer


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def advance_status(request, pk: int):
    configured = getattr(settings, "INTERNAL_API_SECRET", "") or ""
    if not configured:
        return Response(
            {"detail": "INTERNAL_API_SECRET not configured on the server"},
            status=http_status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    if request.headers.get("X-Internal-Secret") != configured:
        return Response(
            {"detail": "forbidden"},
            status=http_status.HTTP_403_FORBIDDEN,
        )

    new_status = request.data.get("status")
    if not new_status:
        return Response(
            {"detail": "status is required"},
            status=http_status.HTTP_400_BAD_REQUEST,
        )

    try:
        order = Order.objects.get(pk=pk)
    except Order.DoesNotExist:
        return Response(
            {"detail": f"order {pk} not found"},
            status=http_status.HTTP_404_NOT_FOUND,
        )

    if order.status == new_status:
        return Response(OrderDetailSerializer(order).data)

    try:
        order.transition_to(new_status)
    except ValueError as exc:
        return Response(
            {"detail": str(exc)},
            status=http_status.HTTP_409_CONFLICT,
        )

    return Response(OrderDetailSerializer(order).data)
