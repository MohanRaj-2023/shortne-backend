from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
import mimetypes

# Create your models here.

class Hashtags(models.Model):
    name=models.CharField(max_length=100,unique=True)

    def __str__(self):
        return self.name
    
def file_size_type_validator(file):
    image_limit = 5 * 1024 * 1024  # 5 MB
    video_limit = 20 * 1024 * 1024  # 20 MB

    mime_type, _ = mimetypes.guess_type(file.name)

    if mime_type:
        if mime_type.startswith('image'):
            if file.size > image_limit:
                raise ValidationError("Image file size must be less than 5 MB.")
            return  # ✅ valid image
        elif mime_type.startswith('video'):
            if file.size > video_limit:
                raise ValidationError("Video file size must be less than 20 MB.")
            return  # ✅ valid video
    raise ValidationError("Unsupported media type. Only images and videos are allowed.")


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
            
