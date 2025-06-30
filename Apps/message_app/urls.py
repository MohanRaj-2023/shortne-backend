from django.urls import path
from .views import get_or_create_chat,ChatMessageView,MarkreadView,get_online_users,UnreadMessageView,ChatListView

urlpatterns = [
    path('create/',get_or_create_chat.as_view(),name='create_or_get_chat'),
    path('chat/<uuid:chat_id>/messages/',ChatMessageView.as_view(),name='chat-view'),
    path('chat/<uuid:chat_id>/mark_read/',MarkreadView.as_view(),name='mark_read'),
    path('online-users/',get_online_users.as_view(),name='user-online'),
    path('unread-counts/',UnreadMessageView.as_view(), name='unread_msg-counts'),
    path('chats/', ChatListView.as_view(), name='chat-list'),
]