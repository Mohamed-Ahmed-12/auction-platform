import asyncio
import queue
import random
import time
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Count
from django.contrib.auth import get_user_model

from django.http import StreamingHttpResponse
from .events_queue import event_queue

from main.models import Auction , Bid

User = get_user_model()
class DashboardView(APIView):
    """
    Dashboard API view
    Returns the auction count for the authenticated user.
    Superusers see all auctions, others only their own.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    def get(self, request):
        today = timezone.now().date()
        auction_count = Auction.objects.count()
        user_count = User.objects.count()
        bids_today = Bid.objects.filter(created_at__date=today).count()
        data = {
            "auction_count": auction_count,
            "user_count":user_count,
            "bids_today":bids_today,
            
        }
        return Response(data)



async def events(request):
    """
    Sends server-sent events to the client.
    """
    async def event_stream():
        while True:
            data = await event_queue.get()
            yield f"data: {data}\n\n"
    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')
