from django.db import models
# from user_app.models import User
from post_app.models import Post
from django.conf import settings

# Create your models here.

# Comment

class Comment(models.Model):
    comment = models.TextField()
    post    = models.ForeignKey(Post,on_delete=models.CASCADE,related_name='comments')
    user    = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True) #can't update
    updated_at = models.DateTimeField(auto_now=True)    #update for each save

# Like Dislike
class PostLikeDislike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    post = models.ForeignKey('post_app.Post',on_delete=models.CASCADE,related_name='like_dislike_post')
    is_like = models.BooleanField() #true-like false-dislike
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user','post')

    def __str__(self):
        return f"{self.user} -> {self.post} " 

# Comment Like dislike
class CommentLikeDislike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment,on_delete=models.CASCADE,related_name='like_dislike_comment')
    is_like = models.BooleanField() #true-like false-dislike
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user','comment')

    def __str__(self):
        return f"{self.user} -> {self.comment} " 
    
# Sharepost

# class SharePost(models.Model):
#     sender = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='shared_by')
#     receiver = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='shared_to')
#     post = models.ForeignKey(Post,on_delete=models.CASCADE)
#     message = models.TextField(blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)

