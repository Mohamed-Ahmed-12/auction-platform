from rest_framework import viewsets
from django_filters import rest_framework as filters
from .models import Category , Auction
from .serializers import CategorySerializer,AuctionSerializer
from .filters import AuctionFilter

class CategoryView(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class AuctionView(viewsets.ModelViewSet):
    queryset = Auction.objects.all()
    serializer_class = AuctionSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = AuctionFilter
