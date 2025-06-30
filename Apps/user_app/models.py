from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
    email=models.EmailField(unique=True,max_length=191)
    username=models.CharField(unique=True,max_length=191)

    USERNAME_FIELD='email'
    REQUIRED_FIELDS=['username']

    def __str__(self):
        return self.username
    


class UserProfile(models.Model):
    user  = models.OneToOneField(User,on_delete=models.CASCADE,related_name='profile')
    bio   = models.TextField(blank=True, default="This user hasn't added a bio yet.")
    image = models.ImageField(blank=True, upload_to='profile_images/',default='profile_images/defaultimg.jpg')
    link  = models.URLField(max_length=200,blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"
   

class Follow(models.Model):
    follower = models.ForeignKey(User,related_name='following',on_delete=models.CASCADE)
    following = models.ForeignKey(User,related_name='followers',on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower','following')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.follower} follows {self.following}"        

    


