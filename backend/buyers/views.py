from rest_framework.generics import RetrieveAPIView
from .models import Buyer
from .serializers import BuyerProfileSerializer


class BuyerProfileView(RetrieveAPIView):
    serializer_class = BuyerProfileSerializer

    def get_object(self) -> Buyer:
        return self.request.user.buyer_profile
