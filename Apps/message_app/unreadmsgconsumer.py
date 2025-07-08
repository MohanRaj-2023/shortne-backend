# unread_message_consumer.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from message_app.models import Message, Chat

class UnreadMessageConsumer(AsyncWebsocketConsumer):
    print("🚨 CONNECTING to UnreadMessageConsumer...")
    async def connect(self):
        print("🚨 UnreadMessageConsumer CONNECT triggered")
        self.user = self.scope["user"]
        print("🔍 WebSocket connected as user:", self.user.id)
        if not self.user.is_authenticated:
            print("❌ Unauthenticated in UnreadMessageConsumer")
            await self.close()
            return

        print(f"🔌 Connected to UnreadMessageConsumer: {self.user}")
        print("🧑 Connected User ID:", self.user.id)
        self.group_name = f'unread_user_{self.user.id}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        
        count = await self.get_unread_count()
        await self.send(text_data=json.dumps({
            "type": "UNREAD_MESSAGE_COUNT_UPDATE",
            "unread_messages": count
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)


    async def unread_message_count(self, event):
        print("📨 unread_message_count RECEIVED in consumer with count:", event['unread_messages'])  # ✅ Debug here
        await self.send(text_data=json.dumps({
            'type': 'UNREAD_MESSAGE_COUNT_UPDATE',
            'unread_messages': event['unread_messages']
        }))

    @database_sync_to_async
    def get_unread_count(self):
        user = self.user
        chats = Chat.objects.filter(user1=user) | Chat.objects.filter(user2=user)
        unread = Message.objects.filter(chat__in=chats, is_read=False).exclude(sender=user)
        return unread.count()
