from channels.generic.websocket import AsyncWebsocketConsumer
import json

class NotificationConsumers(AsyncWebsocketConsumer):
    async def connect(self):
        print("[WebSocket] NotificationConsumer.connect() called")
        print(f"[WebSocket] Connection attempt by user: {self.scope['user']}")
        self.user = self.scope["user"]
        self.group_name = f"user_{self.user.id}"

        try:
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            print(f"[WebSocket] Joined group: {self.group_name}")
        except Exception as e:
            print(f"[WebSocket] ❌ Error joining group: {e}")

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Receive count update
    async def send_notification_count(self, event):
        await self.send(text_data=json.dumps({
            'type': 'NOTIFICATION_COUNT_UPDATE',
            'unread_notifications': event['unread_notifications']
        }))

    # Receive NEW notification and send it to frontend
    async def send_new_notification(self, event):
        print("🎯 Event received in consumer:", event)
        await self.send(text_data=json.dumps({
            'type': 'NEW_NOTIFICATION',
            'notification': event['notification'],  # send full object if needed
            'unread_notifications': event['unread_notifications'],  # new unread count
        }))

