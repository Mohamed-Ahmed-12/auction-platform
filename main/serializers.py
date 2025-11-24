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
        
class ItemsSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    bids = BidSerializer(many=True , read_only = True)
    class Meta:
        model = Item
        fields = ["id", "title","desc","start_price","min_increment","auction","category" , "bids" , "end_at" , "is_active"]


class AuctionSerializer(serializers.ModelSerializer):
    """
    AuctionSerializer with full details.
    """
    status = serializers.SerializerMethodField()
    items = ItemsSerializer(many=True , read_only = True)
    class Meta:
        model = Auction
        fields = ['id','title','slug','desc','entry_fee','start_date','end_date','status','items']
        
    def get_status(self,obj):
        now = timezone.now()
        if obj.end_date<now: return "ended"
        elif obj.start_date>now: return "upcoming"
        return "live"

class AuctionBasicDetailsSerializer(AuctionSerializer):
    """
    A lightweight version of AuctionSerializer without nested items.
    """
    class Meta(AuctionSerializer.Meta):
        fields = ['id','title','slug','desc','entry_fee','start_date','end_date','status',]

 
