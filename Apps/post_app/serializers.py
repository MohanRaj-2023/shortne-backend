from rest_framework import serializers
from post_app.models import Post
from user_app.models import User

from user_app.models import UserProfile
from interaction_app.models import PostLikeDislike
from user_app.models import Follow

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['image']

# user search serializer.

class UserSearchSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(source='profile.image')  # assuming OneToOne link
    posts_count = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'image','posts_count','followers_count','following_count']
    
    def get_posts_count(self, obj):
        return Post.objects.filter(user=obj.id).count()

    def get_followers_count(self, obj):
        return Follow.objects.filter(following=obj.id).count()

    def get_following_count(self, obj):
        return Follow.objects.filter(follower=obj.id).count()

class PostSerializer(serializers.ModelSerializer):
    hashtags = serializers.StringRelatedField(many=True)
    username = serializers.CharField(source='user.username',read_only=True)

    profileimage = ProfileSerializer(source='user.profile',read_only=True)
    
    is_like = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    dislike_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id','caption','hashtags','media','media_type','created_at','user','username','profileimage','is_like','like_count','dislike_count']
    
    def get_is_like(self,post):
        user = self.context.get('request').user
        if user.is_authenticated:
            try:
                like = PostLikeDislike.objects.get(user=user,post=post)
                return like.is_like
            except PostLikeDislike.DoesNotExist:
                return None
        return None
    
    def get_like_count(self, post):
        return PostLikeDislike.objects.filter(post=post, is_like=True).count()

    def get_dislike_count(self, post):
        return PostLikeDislike.objects.filter(post=post, is_like=False).count()

