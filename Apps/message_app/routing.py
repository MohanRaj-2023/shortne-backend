from django.urls import path
from message_app import consumers, unreadmsgconsumer
from notification_app import Notificationconsumer

websocket_urlpatterns = [
    path("ws/chat/global/",unreadmsgconsumer.UnreadMessageConsumer.as_asgi()),
    path("ws/notifications/", Notificationconsumer.NotificationConsumers.as_asgi()),
    path("ws/chat/<str:chat_id>/", consumers.ChatConsumer.as_asgi())
]
