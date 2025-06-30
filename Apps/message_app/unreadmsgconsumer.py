# unread_message_consumer.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from message_app.models import Message, Chat

class UnreadMessageConsumer(AsyncWebsocketConsumer):
    print("🚨 CONNECTING to UnreadMessageConsumer...")
    async def connect(self):
        self.user = self.scope["user"]
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

    # async def receive(self, text_data):
    #     data = json.loads(text_data)
    #     print("🎯 UnreadMessageConsumer.receive() received data:", data)
    #     # msg_type = data.get("type")

    #     # if msg_type == "get_unread_count":
    #     #     print("📥 get_unread_count received in UnreadMessageConsumer")
    #     #     count = await self.get_unread_count()
    #     #     await self.send(text_data=json.dumps({
    #     #         "type": "UNREAD_MESSAGE_COUNT",
    #     #         "unread_messages": count
    #     #     }))

    async def unread_message_count(self, event):
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
