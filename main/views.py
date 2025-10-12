from rest_framework import viewsets
from .models import Category , Auction
from .serializers import CategorySerializer,AuctionSerializer

class CategoryView(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class AuctionView(viewsets.ModelViewSet):
    queryset = Auction.objects.all()
    serializer_class = AuctionSerializer
