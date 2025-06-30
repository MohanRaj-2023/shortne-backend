from django.db import models
from django.conf import settings
from post_app.models import Post
# Create your models here.

class Notification(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='sent_notification',on_delete=models.CASCADE)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='received_notification',on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)  # ✅ Add this line
    message = models.TextField()
    notification_type = models.CharField(max_length=100)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} -> {self.receiver} [{self.notification_type}]"
