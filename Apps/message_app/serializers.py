from rest_framework import serializers
from message_app.models import Message,Chat
from user_app.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['id','username']


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model=Message
        fields = '__all__'

class ChatListSerializer(serializers.ModelSerializer):
    friend = serializers.SerializerMethodField()
    last_message = MessageSerializer()

    class Meta:
        model = Chat
        fields = ['id', 'friend', 'last_message']

    def get_friend(self, obj):
        user = self.context['request'].user
        return UserSerializer(obj.user2 if obj.user1 == user else obj.user1).data