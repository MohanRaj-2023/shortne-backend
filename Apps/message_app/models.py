from django.db import models
from django.contrib.auth import get_user_model
import uuid
from post_app.models import Post
# Create your models here.



User = get_user_model()

class Chat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chats_initiated')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chats_received')
    last_message = models.ForeignKey('Message', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        unique_together = ('user1', 'user2')  # Prevent duplicate chats

    def __str__(self):
        return f"Chat between {self.user1.username} and {self.user2.username}"

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    is_post_share = models.BooleanField(default=False)
    post = models.ForeignKey(Post, null=True, blank=True, on_delete=models.SET_NULL)
    shared_post_description = models.TextField(blank=True)
    shared_post_media = models.URLField(blank=True)
    shared_post_media_type = models.CharField(max_length=10, blank=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
