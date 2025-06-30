from rest_framework import serializers
from interaction_app.models import Comment
from user_app.models import UserProfile
from interaction_app.models import CommentLikeDislike

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model=UserProfile
        fields=['image']

class CommentSerializer(serializers.ModelSerializer):
    profileimage = ProfileSerializer(source='user.profile',read_only=True)
    username = serializers.CharField(source='user.username',read_only=True)
    is_like = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    dislike_count = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields= ['id','comment','post','user','username','profileimage','created_at','updated_at','is_like','like_count','dislike_count']
    
    def get_is_like(self,comment):
        user = self.context.get('request').user
        if user.is_authenticated:
            try:
                like = CommentLikeDislike.objects.get(user=user,comment=comment)
                print("Like_Serialized:",like)
                return like.is_like
            except CommentLikeDislike.DoesNotExist:
                return None
        return None
    def get_like_count(self, comment):
        return CommentLikeDislike.objects.filter(comment=comment, is_like=True).count()

    def get_dislike_count(self, comment):
        return CommentLikeDislike.objects.filter(comment=comment, is_like=False).count()