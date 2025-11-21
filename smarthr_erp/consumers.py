# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Create a group for real-time notifications
        self.room_group_name = "notifications_group"

        # Join the notifications group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave the notifications group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Receive message from WebSocket (optional)
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message')

        # Send message to WebSocket (if needed)
        await self.send(text_data=json.dumps({
            'message': message
        }))

    async def send_notification(self, event):
        # Send notification to WebSocket
        await self.send(text_data=json.dumps({
            'notification': event['message']
        }))
