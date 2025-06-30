from django.shortcuts import render
from rest_framework.views  import APIView
from rest_framework.response  import Response
from notification_app.models import Notification
from user_app.models import User
from rest_framework.permissions import IsAuthenticated
from .serializers import NotificationSerializer

from message_app.models import Message,Chat

# real time notification count
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

# Create your views here.


class NotificatiinView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            user =  User.objects.get(username=request.user)
            notifications = Notification.objects.filter(receiver=user,is_read=False)
            serializer = NotificationSerializer(notifications,many=True)
            return Response({"details":serializer.data})
        except Exception as error:
            print("Notification_Error:",error)
            return Response({"details":str(error)})
        
class DeleteNotificationView(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self,request):
        try:
            id=request.query_params.get('id')
            print("ID:",id)
            Notification.objects.get(id=id).delete()
            # ✅ After delete, send updated count
            unread_count = Notification.objects.filter(receiver=request.user, is_read=False).count()
            channel_layer = get_channel_layer()
            group_name = f"user_{request.user.id}"

            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    'type': 'send_notification_count',
                    'unread_notifications': unread_count,
                }
            )

            return  Response({"details":"Notification deleted successfully...!"})
        except Exception as error:
            return Response({"details":str(error)})

class UnreadCoutView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        user = request.user
        
        # Get all chats the user is part of
        chats = Chat.objects.filter(user1=user) | Chat.objects.filter(user2=user)

        unread_message_count = 0
        for chat in chats:
            # Get messages in this chat not sent by the user and not read
            messages = Message.objects.filter(
                chat=chat,
                is_read=False
            ).exclude(sender=user)

            unread_message_count += messages.count()
        unread_notifications = Notification.objects.filter(receiver=user, is_read=False).count()

            # 
        channel_layer = get_channel_layer()
        group_name = f"user_{request.user.id}"

        async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    'type': 'send_notification_count',
                    'unread_notifications': unread_notifications,
                }
            )
        
        return Response({
                'unread_messages': unread_message_count,
                'unread_notifications': unread_notifications
            })
        
class MarkReadView(APIView):
    permission_classes=[IsAuthenticated]
    def patch(self,request):
        user = request.user
        id = request.data.get('id')
        notification=Notification.objects.get(id=id)
        notification.is_read=True
        notification.save()
        
        # Count remaining unread notifications
        unread_count = Notification.objects.filter(receiver=request.user, is_read=False).count()

        # Send updated count to WebSocket channel
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{request.user.id}",
            {
                "type": "send_notification_count",
                "unread_notifications": unread_count
            }
        )
        print("Notification:",notification.is_read)
        return Response({"details":"Read success"})