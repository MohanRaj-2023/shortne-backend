from rest_framework import serializers
from django.contrib.auth import get_user_model
# Models
from user_app.models import UserProfile,Follow
from post_app.models import Post

User = get_user_model()

class SignupSerializer(serializers.ModelSerializer):

    class Meta:
        model= User
        fields=['email','username','password']
        extra_kwargs = {
            'password':{'write_only':True}
        }

    def validate(self, data):
        errors={}
        Email=data.get('email')
        if User.objects.filter(email=Email).exists():
            errors['email']='Email already exists'
        
        Username=data.get('username')
        if User.objects.filter(username=Username).exists():
            errors['username'] = 'Username already exists'

        if errors:
            raise serializers.ValidationError(errors)
        
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    username =  serializers.CharField(source = 'user.username', read_only=True)
    posts_count = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    class Meta:
        model = UserProfile
        fields = ['id','image','bio','link','user','username','posts_count','followers_count','following_count']

    def get_posts_count(self, obj):
        return Post.objects.filter(user=obj.user).count()

    def get_followers_count(self, obj):
        return Follow.objects.filter(following=obj.user).count()

    def get_following_count(self, obj):
        return Follow.objects.filter(follower=obj.user).count()

class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model= Follow
        fields = '__all__'