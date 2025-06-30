# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.conf import settings
# # from interaction_app.models import SharePost
# from notification_app.models import Notification


# @receiver(post_save,sender=SharePost)
# def send_share_post_notification(sender,instance,created,**kwargs):
#     if created:
#         sender = instance.sender
#         receiver = instance.receiver
#         print("share signal trigered....")
#         Notification.objects.create(
#             sender=sender,
#             receiver=receiver,
#             message=f"{sender.username} shared a post.",
#             notification_type="share_post"
#         )