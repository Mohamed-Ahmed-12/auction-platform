from django.utils import timezone
from rest_framework import serializers
from .models import Category , Auction , Item , Bid

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"
        
class BidSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bid
        fields = "__all__"
        
class AuctionItemsSerializer(serializers.ModelSerializer):
    bids = BidSerializer(many=True , read_only = True)
    class Meta:
        model = Item
        fields = "__all__"
   
class AuctionSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    items = AuctionItemsSerializer(many=True , read_only = True)
    class Meta:
        model = Auction
        fields = ['title','slug','desc','entry_fee','start_date','end_date','status','items']
    def get_status(self,obj):
        now = timezone.now()
        if obj.end_date<now: return "ended"
        elif obj.start_date>now: return "upcoming"
        return "live"

