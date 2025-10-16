import json
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from main.models import Item

class BidConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Get the unique ID from the URL path
        self.item_id = self.scope['url_route']['kwargs']['item_id']
        item = await self.get_item(id=self.scope['url_route']['kwargs']['item_id'])
        if item is None:
            await self.accept()
            await self.close(code=4001,reason="Item not found")  # Custom close code for "item not found"
            return
        # Create a unique group name for this specific auction
        self.group_name = 'auction_item_%s' % self.item_id

        # Add this consumer to the Group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name # The unique identifier for this consumer connection
        )
        
        await self.accept()
        # Now, the consumer is officially listening to 'auction_item_123'

    async def disconnect(self, close_code):
        print(close_code)
        # await self.channel_layer.group_discard(
        #     self.group_name,
        #     self.channel_name
        # )

    async def receive(self, text_data):
        data = json.loads(text_data)
        print(data)
        bid_amount = data['bid']

        # Broadcast bid to group
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'broadcast_bid', #This specifies which method on the consumers in the group should be called to handle this message.
                'bid': bid_amount,
            }
        )
        
    async def broadcast_bid(self, event):
        """
        The method receives a dictionary named event (which is the message payload sent by group_send).
        """
        await self.send(text_data=json.dumps({
            'bid': event['bid'],
        }))

    async def get_item(self, id):
        try:
            return await database_sync_to_async(Item.objects.get)(id=id)
        except Item.DoesNotExist:
            return None

