from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.db import database_sync_to_async

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # We can use the user's ID to create a unique private group for them
        user = self.scope['user']
        if user.is_anonymous:
            # Reject anonymous connections if necessary
            await self.close()
            return

        self.user_id = user.id
        self.group_name = f'user_notifications_{self.user_id}'

        # Add the channel to the user's private notification group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()
        print(f"User {self.user_id} connected to notifications.")

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
        print(f"Disconnected from notifications with code: {close_code}")

    # Receive message from the group
    async def send_notification(self, event):
        """
        Handler for sending notification events to the client.
        The 'event' dict should contain a 'message' key.
        """
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': event['type'], # e.g., 'new_bid', 'auction_end', 'user_joined'
            'message': event['message'],
            'data': event.get('data', {}) # Optional extra data
        }))