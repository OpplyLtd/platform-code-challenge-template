from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ingredients.models import Ingredient

from .models import Order, OrderItem
from .serializers import (
    OrderCreateSerializer,
    OrderDetailSerializer,
    OrderSerializer,
)
from .services import publish_order_transitioned


class OrderListCreateView(ListCreateAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(buyer=self.request.user.buyer_profile).prefetch_related("items")

    def create(self, request: Request, *args, **kwargs) -> Response:
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        buyer = request.user.buyer_profile
        order = Order.objects.create(buyer=buyer)

        for item_data in serializer.validated_data["items"]:
            ingredient = Ingredient.objects.get(pk=item_data["ingredient_id"])
            OrderItem.objects.create(
                order=order,
                ingredient=ingredient,
                quantity=item_data["quantity"],
                unit_price=ingredient.price_per_unit,
            )

        out = OrderDetailSerializer(order)
        return Response(out.data, status=status.HTTP_201_CREATED)


class OrderDetailView(RetrieveAPIView):
    serializer_class = OrderDetailSerializer

    def get_queryset(self):
        return Order.objects.filter(buyer=self.request.user.buyer_profile).prefetch_related(
            "items__ingredient__supplier"
        )


class OrderTransitionView(APIView):
    def post(self, request: Request, pk: int) -> Response:
        order = Order.objects.get(pk=pk, buyer=request.user.buyer_profile)
        new_status = request.data.get("status")
        if not new_status:
            return Response({"detail": "status is required."}, status=status.HTTP_400_BAD_REQUEST)

        previous_status = order.status
        try:
            order.transition_to(new_status)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        if previous_status == "CONFIRMED" and order.status == "PROCESSING":
            publish_order_transitioned(order, previous_status)

        return Response(OrderDetailSerializer(order).data)
