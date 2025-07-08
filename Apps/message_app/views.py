from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from message_app.models import Chat,Message
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from .serializers import MessageSerializer,ChatListSerializer

# post model
from post_app.models import Post

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from django.core.cache import cache
from django_redis import get_redis_connection
# Create your views here.

User=get_user_model()

class get_or_create_chat(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            user1 = request.user
            user2_id = request.data.get('user2_id')            
            
            user2 = User.objects.get(id=user2_id)
            
            user_a,user_b = sorted([user1,user2], key=lambda x:x.id)

            if user_a==user_b:
                return Response({"details":"You can't chat with yourself."})

            chat,created = Chat.objects.get_or_create(user1=user_a,user2=user_b) 
            print("Chat_id:",str(chat.id))
            print("Created:",created)

            return Response({
                "chat_id":chat.id,
                "created":created
            })
        except User.DoesNotExist:
            return Response({"details":"User does not exist"})
        except Exception as error:
            return Response({"details":str(error)})
        
# fetch chat 
class ChatMessageView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request,chat_id):
        try:
            chat = Chat.objects.get(id=chat_id)
            Messages= Message.objects.filter(chat=chat).order_by('timestamp')
            serializer=MessageSerializer(Messages,many=True)
            # print("Message:",serializer.data)
            return Response(serializer.data)
        except Exception as error:
            print("Error:",error)
            return Response({"details":str(error)})

# mark_read
class MarkreadView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request,chat_id):
        user = request.user
        chat = Chat.objects.get(id=chat_id)
        try:
            messages_to_mark = Message.objects.filter(chat=chat,is_read=False).exclude(sender=user)
            message_ids = list(messages_to_mark.values_list("id", flat=True))
            messages_to_mark.update(is_read=True)
            # after marking messages as read
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'chat_{chat.id}',  # same group name as in WebSocket
                {
                    'type': 'mark_messages_read',
                    'message_ids': message_ids,
                }
            )
            # print("READ:",messages_to_mark)
            
            return Response({"read_count:",messages_to_mark})
        except Exception as e:
            print("Error:",e)
            return Response({"Error:",str(e)})
        

class get_online_users(APIView):
    permission_classes=[IsAuthenticated]
    
    def get(self, request):
        try:
            redis_conn = get_redis_connection("default")
            pattern = "user_online:*"
            keys = redis_conn.keys(pattern)

            user_ids = [int(key.decode().split(":")[1]) for key in keys]
            online_users = User.objects.filter(id__in=user_ids).values("id", "username")

            return Response({"online_users": list(online_users)})
        except Exception as e:
            print("Redis error:", e)
            return Response({"online_users": []})

class UnreadMessageView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        user = request.user
        # Get all chats where current user is a participant
        user_chats = Chat.objects.filter(user1=user) | Chat.objects.filter(user2=user)

        # Unread messages NOT sent by the current user
        unread_messages = Message.objects.filter(
            chat__in=user_chats,
            is_read=False
        ).exclude(sender=user)

        unread_map = {}

        for msg in unread_messages:
            chat = msg.chat
            other_user = chat.user1 if chat.user2 == user else chat.user2
            if other_user.id in unread_map:
                unread_map[other_user.id] += 1
            else:
                unread_map[other_user.id] = 1

        return Response(unread_map)
    

class ChatListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        chats = Chat.objects.filter(user1=user) | Chat.objects.filter(user2=user)
        chats = chats.select_related('last_message').order_by('-last_message__timestamp')

        serializer = ChatListSerializer(chats, many=True, context={'request': request})
        return Response(serializer.data)
    

