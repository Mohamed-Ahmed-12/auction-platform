from rest_framework import viewsets
from django_filters import rest_framework as filters
from .models import Category , Auction , Item
from .serializers import CategorySerializer,AuctionBasicDetailsSerializer,AuctionSerializer , ItemsSerializer
from .filters import AuctionFilter

class CategoryView(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class AuctionView(viewsets.ModelViewSet):
    queryset = Auction.objects.all()
    serializer_class = AuctionBasicDetailsSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = AuctionFilter
    lookup_field = "slug"
    def get_serializer_class(self):
        if self.action =="retrieve":
            return AuctionSerializer
        return super().get_serializer_class()

class AuctionItemsView(viewsets.ModelViewSet):
    queryset = Item.objects.filter(is_active=True)
    serializer_class = ItemsSerializer
