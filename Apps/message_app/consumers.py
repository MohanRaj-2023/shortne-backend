import json
from channels.generic.websocket import AsyncWebsocketConsumer
from message_app.models import Message,Chat
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async

from django_redis import get_redis_connection
from urllib.parse import parse_qs
from django.db.models import Q


User=get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
            self.user = self.scope["user"]
            print("Connected_user:", self.user.id)
            self.chat_id = self.scope['url_route']['kwargs']['chat_id']
            self.room_group_name = f'chat_{self.chat_id}'

            # 🔍 Get `target_id` (receiver's ID) from query string
            query_string = self.scope['query_string'].decode()
            query_params = parse_qs(query_string)
            target_id = query_params.get('target_id', [None])[0]
            self.target_user_id = int(target_id) if target_id else None

            await self.channel_layer.group_add(f"user_{self.user.id}", self.channel_name) #personal chat
            await self.channel_layer.group_add(self.room_group_name, self.channel_name) #chat group name

            await self.accept()  # Always accept after group add

            if self.user and self.user.is_authenticated:
                await self.add_online_user(self.user.id)

                # ✅ Notify group: this user is online
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "user_status",
                        "user_id": self.user.id,
                        "is_online": True,
                    }
                )

                # ✅ Send receiver's (target user) status to this user
                if self.target_user_id:
                    is_online = await self.is_user_online(self.target_user_id)
                    await self.send(text_data=json.dumps({
                        "type": "user_status",
                        "user_id": self.target_user_id,
                        "is_online": is_online
                    }))

    async def chat_alert(self, event):
            await self.send(text_data=json.dumps({
                'type': 'chat_alert',
                'chat_id': event['chat_id'],
                'from_user_id': event['from_user_id'],
            }))        
                

####################
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(f"user_{self.user.id}", self.channel_name)
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        
        if self.user and self.user.is_authenticated:
            await self.remove_online_user(self.user.id)
            # Notify group user is offline
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "user_status",
                    "user_id": self.user.id,
                    "is_online": False,
                }
            )
    
    
    # ✅ Add or refresh the user online key with expiry
    async def add_online_user(self, user_id):
        from asgiref.sync import sync_to_async

        @sync_to_async
        def _set():
            redis_conn = get_redis_connection("default")
            redis_conn.set(f"user_online:{user_id}", 1, ex=60)  # 60 sec TTL
        await _set()


    
    # ✅ Remove the user online key manually
    async def remove_online_user(self, user_id):
        from asgiref.sync import sync_to_async

        @sync_to_async
        def _delete():
            redis_conn = get_redis_connection("default")
            redis_conn.delete(f"user_online:{user_id}")
        await _delete()

    async def user_status(self, event):
        # Send real-time status to frontend
        await self.send(text_data=json.dumps({
            'type': 'user_status',
            'user_id': event['user_id'],
            'is_online': event['is_online']
        }))
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        print("🎯 ChatConsumer.receive() received data:", data)
        msg_type = data.get("type")
        if msg_type == "get_unread_count":
            print("🚨 Misrouted to ChatConsumer — should hit UnreadMessageConsumer")
            return
        
        # ✅ Handle heartbeat
        if data.get("type") == "heartbeat":
            if self.user and self.user.is_authenticated:
                await self.add_online_user(self.user.id)  # Refresh TTL
            return

        # ✅ Guard: only process if it's a chat message
        if "message" not in data or "sender" not in data:
            print("Invalid message format or missing fields.")
            return
        
        message = data['message']
        sender = data['sender']
        is_post_share = data.get("is_post_share", False)
        post_data = data.get("post",None) 
        print("Post:",post_data)
        print("Message:",message)
        print("Sender:",sender)

        # Save to DB
        try:
            chat = await database_sync_to_async(Chat.objects.get)(id=self.chat_id)
            sender = await database_sync_to_async(User.objects.get)(username=sender)
        except Exception as e:
            print("Chat/User error:", e)
            return

        try:
            new_message = await database_sync_to_async(Message.objects.create)(
                chat=chat,
                sender=sender,
                content=message,
                is_post_share=is_post_share,
                post_id=post_data["id"] if post_data else None,  # link to actual Post model if needed
                shared_post_description=post_data["description"] if post_data else "",
                shared_post_media=post_data["media"] if post_data else "",
                shared_post_media_type=post_data["media_type"] if post_data else ""
            )

            await database_sync_to_async(lambda: chat.__class__.objects.filter(id=chat.id).update(last_message=new_message))()

            print("New message.....................")
            # After saving `new_message`
            if sender.id != self.target_user_id:
                # Count unread messages for the receiver
                unread_count = await database_sync_to_async(
                    lambda: Message.objects.filter(
                        Q(chat__user1_id=self.target_user_id) | Q(chat__user2_id=self.target_user_id),
                        is_read=False
                    ).exclude(sender_id=self.target_user_id).count()
                )()

                # Send unread count notification
                print("📡 Sending unread count to:", self.target_user_id)
                await self.channel_layer.group_send(
                    f'unread_user_{self.target_user_id}',
                    {
                        'type': 'unread_message_count',
                        'unread_messages': unread_count,
                    }
                )
            
        except Exception as e:
                print("DB Error:", e)
                return
        
    
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender.username,
                'sender_id': sender.id,
                'message_id': new_message.id,
                'chat': str(chat.id),
                'post':post_data
            }
        )

        if sender.id != self.target_user_id:
            # Notify only if receiver is NOT in the same chat room
            await self.channel_layer.group_send(
                f"chat_user{self.target_user_id}",  # personal channel
                {
                    'type': 'chat_alert',
                    'chat_id': self.chat_id,
                    'from_user_id': sender.id,
                }
            )


    async def chat_alert(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_alert',
            'chat_id': event['chat_id'],
            'from_user_id': event['from_user_id'],
        }))


    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
        'type': 'chat_message',
        'message': event['message'],
        'sender': event['sender'],
        'sender_id': event['sender_id'],  # ✅ add this
        'message_id': event['message_id'],  # ✅ add this too for marking read
        'chat': event['chat'],
        'post_id': event.get('post_id')
    }))



    # consumers.py
    async def mark_messages_read(self, event):
        await self.send(text_data=json.dumps({
            'type': 'mark_messages_read',
            'message_ids': event['message_ids'],
        }))
  

    async def is_user_online(self, user_id):
        from asgiref.sync import sync_to_async
        from django_redis import get_redis_connection
        # Update your check:
        @sync_to_async
        def _check():
            redis_conn = get_redis_connection("default")
            return redis_conn.exists(f"user_online:{user_id}")

        return await _check()
