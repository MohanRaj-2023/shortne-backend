from rest_framework import serializers
from notification_app.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    from_user_username = serializers.CharField(source='sender.username', read_only=True)
    post_id = serializers.IntegerField(source='post.id', required=False, allow_null=True)

    class Meta:
        model = Notification
        fields = ['id','sender','from_user_username','message','post_id','notification_type','is_read','created_at']
    