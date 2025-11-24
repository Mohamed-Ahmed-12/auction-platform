from datetime import datetime
from decimal import Decimal, InvalidOperation
import json
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from main.models import Item, Bid , AuctionResult
from main.serializers import BidSerializer

class BidConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.item_id = self.scope['url_route']['kwargs']['item_id']
        self.group_name = f'auction_item_{self.item_id}'
        
        item = await self.get_item(id=self.item_id)

        # If item obj not found
        if item is None:
            await self.accept()
            await self.close(code=4001, reason="Item not found")
            return
        
        # If item obj already ended not accept any connection
        if item.end_at is not None:
            await self.accept()
            await self.close(code=4001, reason="Item was ended")
            return

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        print(f"Disconnected with code: {close_code}")
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        # load the bid amount
        try:
            data = json.loads(text_data)
            bid_amount = Decimal(str(data.get('amount')))
        except (json.JSONDecodeError, InvalidOperation, TypeError):
            await self.send(text_data=json.dumps({
                'error': 'Invalid bid format'
            }))
            return

        item = await self.get_item(id=self.item_id)
        if item is None:
            await self.send(text_data=json.dumps({
                'error': 'Item not found'
            }))
            return

        if not item.is_active:
            await self.send(text_data=json.dumps({
                'error': 'Item is inactive'
            }))
            return

        min_inc = item.min_increment
        last_bid = await self.last_bid(itemId=self.item_id)
        current_price = last_bid.amount if last_bid else item.start_price
        min_acceptable_bid = current_price + min_inc

        print(f"Minimum acceptable bid: {min_acceptable_bid}")

        if bid_amount < min_acceptable_bid:
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'broadcast_bid',
                    'error': True,
                    'message': json.dumps({
                        'error': f'Bid must be at least {min_acceptable_bid:.2f}'
                    })
                }
            )
            return

        try:

            bid_obj = await database_sync_to_async(Bid.objects.create)(
                item=item,
                amount=bid_amount,
                created_by=self.scope['user']
            )

            serialized_bid = await database_sync_to_async(lambda: BidSerializer(bid_obj).data)()
            
            # Close auction if reserve price is met
            await self.close_auction(item, self.scope['user'], bid_amount)

            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'broadcast_bid',
                    'bid': serialized_bid
                }
            )

        except Exception as e:
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'broadcast_bid',
                    'error': True,
                    'message': json.dumps({
                        'error': 'Failed to place bid',
                        'details': str(e)
                    })
                }
            )

    async def broadcast_bid(self, event):
        if event.get('error'):
            await self.send(text_data=event['message'])
        else:
            await self.send(text_data=json.dumps({
                'bid': event['bid']
            }))

    async def get_item(self, id):
        try:
            return await database_sync_to_async(Item.objects.get)(id=id)
        except Item.DoesNotExist:
            return None

    async def last_bid(self, itemId):
        return await database_sync_to_async(
            lambda: Bid.objects.filter(item_id=itemId).order_by('-created_at').first()
        )()
        
    async def close_auction(self, item, winner, winning_bid):
        item.is_active = False
        item.end_at = datetime.now()
        await database_sync_to_async(item.save)()
        await database_sync_to_async(AuctionResult.objects.create)(
            item=item,
            winner=winner,
            winning_bid=winning_bid
        )
