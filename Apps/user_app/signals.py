from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver
from django.conf import settings
from .models import UserProfile
from .models import Follow
from notification_app.models import Notification
from notification_app.serializers import NotificationSerializer
# web socket
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

#to caseate user profile when the account creare
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


@receiver(post_save,sender=Follow)
def send_follow_notification(sender,instance,created,**kwargs):

    if created:
        follower = instance.follower
        following = instance.following

        print(f"{follower.username} followed {following.username}")

        notification= Notification.objects.create(
            sender = follower,
            receiver = following,
            notification_type='follow',
            message = f"{follower.username} started following you."
        )
        
        # 2. Count total unread
        unread_count = Notification.objects.filter(receiver=following, is_read=False).count()

        # 3. Send real-time update
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{following.id}",
            {
                "type": "send_new_notification",  # calls this method in NotificationConsumer
                "notification":NotificationSerializer(notification).data,
                "unread_notifications": unread_count
            }
        )

@receiver(post_delete,sender=Follow)
def delete_follow_notification(sender,instance,**kwargs):
    Notification.objects.filter(
        sender    = instance.follower,
        receiver  = instance.following,
        notification_type='follow'
    ).delete()