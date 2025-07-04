from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
import mimetypes

# Create your models here.

class Hashtags(models.Model):
    name=models.CharField(max_length=100,unique=True)

    def __str__(self):
        return self.name
    


class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    caption = models.TextField(blank=True)
    hashtags=models.ManyToManyField(Hashtags,blank=True)
    media =  models.URLField()
    media_type=models.CharField(max_length=100,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self,*args,**kwargs):
        if self.media:
            mime_type, _ = mimetypes.guess_type(self.media) 
        if mime_type:
            if mime_type.startswith('image'):
                self.media_type='image'
            elif mime_type.startswith('video'):
                self.media_type='video'
        super().save(*args,**kwargs)

    def __str__(self):
        return f"{self.user}'s post"
            
