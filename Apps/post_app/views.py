from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from post_app.models import Hashtags,Post
from user_app.models import User,UserProfile
from interaction_app.models import PostLikeDislike

from user_app.models import Follow
from notification_app.models import Notification
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

#permission class
from rest_framework.permissions import IsAuthenticated,AllowAny

#serializer
from post_app.serializers import PostSerializer,UserSearchSerializer
from notification_app.serializers import NotificationSerializer
import mimetypes

# pagination
from rest_framework.pagination import CursorPagination

# search
from django.db.models import Q

# cloudinary
import cloudinary.uploader
from cloudinary.uploader import destroy
from urllib.parse import urlparse

import traceback
# Create your views here.

class PostPagination(CursorPagination):
    page_size = 10
    ordering = '-created_at'


class HashtagSearchView(APIView):
    def get(self,request):
        query = request.GET.get('q','')
        if query:
            hashtags = Hashtags.objects.filter(name__icontains=query)[:10]
            result=[{'id':tag.id,
                     'name':tag.name,
                    }
                    for tag in hashtags]
            return Response(result)
        return Response([])
# notifiy user on post
def notify_followers_on_post(post):
    user = post.user
    followers = Follow.objects.filter(following=user).values_list('follower', flat=True)
    channel_layer = get_channel_layer()

    for follower_id in followers:
        notification= Notification.objects.create(
            sender=user,
            receiver_id=follower_id,
            message=f"{user.username} created a new post.",
            notification_type='new_post',
            post=post
        )

         # 2. Count total unread notifications for the follower
        unread_count = Notification.objects.filter(receiver_id=follower_id, is_read=False).count()

        # 3. Send real-time notification to WebSocket group
        async_to_sync(channel_layer.group_send)(
            f"user_{follower_id}",  # matches your NotificationConsumers group
            {
                "type": "send_new_notification",
                "notification":NotificationSerializer(notification).data,
                "unread_notifications": unread_count
            }
        )

class PostCreateView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self, request):
        try:
            user = request.user
            if user is not None:
                file = request.FILES.get('media')
                if not file:
                    return Response({"error": "No media file uploaded"}, status=400)

                # Custom size limits
                image_limit = 5 * 1024 * 1024  # 5 MB
                video_limit = 9 * 1024 * 1024  # 9 MB

                file_name = getattr(file, 'name', None)
                if not file_name:
                    return Response({"error": "Invalid file upload. No filename found."}, status=400)

                mime_type, _ = mimetypes.guess_type(file_name)

                print("DEBUG: file type:", type(file))
                print("DEBUG: file name:", getattr(file, 'name', 'No name'))
                print("DEBUG: file size:", getattr(file, 'size', 'No size'))


                
                if mime_type:
                    if mime_type.startswith('image') and file.size > image_limit:
                        return Response({"error": "Image must be less than 5MB"}, status=status.HTTP_400_BAD_REQUEST)
                    elif mime_type.startswith('video') and file.size > video_limit:
                        return Response({"error": "Video must be less than 10MB"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"error": "Unsupported file type"}, status=status.HTTP_400_BAD_REQUEST)

                # Upload to Cloudinary manually
                upload_result = cloudinary.uploader.upload(file,resource_type='auto')
                resource_type = upload_result.get("resource_type") 

                cloudinary_url = upload_result.get('secure_url')

                post = Post.objects.create(
                    user=user,
                    caption=request.data.get('description'),
                    media=cloudinary_url,
                    media_type=resource_type
                )

                print("Media URL:",cloudinary_url)
                print("Media_type:",post.media_type)

                # ✳️ Process comma-separated hashtag string
                raw_hashtags = request.data.get('query', '')
                tag_names = [tag.strip().lstrip('#') for tag in raw_hashtags.split(',') if tag.strip()]
                hashtag_objs = []

                for name in tag_names:
                    tag, created = Hashtags.objects.get_or_create(name=name)
                    hashtag_objs.append(tag)

                post.hashtags.set(hashtag_objs)
                post.save()
                # send notification
                notify_followers_on_post(post)

                return Response({"details": "Post Created Successfully...!"})
            else:
                return Response({"error": "Invalid user"}, status=401)

        except Exception as error:
            print("Error:", error)
            traceback.print_exc()
            return Response({"error": str(error)}, status=500)


# User Posts
class PostsView(APIView):
    permission_classes=[IsAuthenticated]
    pagination_class = PostPagination

    def get(self,request):
        username=request.query_params.get('username')
        # username=request.data.get('username')
        user=User.objects.get(username=username)
        try:
            posts=Post.objects.filter(user=user)
            paginator = self.pagination_class()
            paginated_posts = paginator.paginate_queryset(posts, request)

            if posts.exists():
                serializer = PostSerializer(paginated_posts,many=True,context={"request":request})
                return paginator.get_paginated_response(serializer.data)
            else:
                return Response({"details":"User did not create any post yet."})
        except Exception as error:
            print("POST_ERROR:",error)
            return Response({'details':'Cant fetch any post'})


class PostView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request,post_id):
        try:
            user=request.user
            post=Post.objects.get(id=post_id)
            print("View_post:",post)
            if post != None:
                serializer = PostSerializer(post,context={"request":request})
                return Response(serializer.data)
            else:
                return Response({"details":"User did not create any post yet."})
        except Exception as error:
            return Response({'details':str(error)})
        
# Home Feeds
class GetPosts(APIView):
    permission_classes=[IsAuthenticated]
    pagination_class = PostPagination
    def get(self,request):
        current_user = request.user
        try:
            Posts = Post.objects.exclude(user=current_user)

            paginator = self.pagination_class()
            paginated_posts = paginator.paginate_queryset(Posts, request)
            # print("POSTS:",Posts)
            if Posts!=None:
                serializer=PostSerializer(paginated_posts,many=True,context={"request":request})
                return paginator.get_paginated_response(serializer.data)
            else:
                return Response({"details":"Loading....."})
        except Exception as error:
            print("Get post ERROR:",error)
            return Response({"details":str(error)})
        
# Video  posts
class VideoPostsView(APIView):
    pagination_class = PostPagination
    permission_classes=[IsAuthenticated]
    def get(self,request):
        try:
            Posts = Post.objects.filter(media_type='video').exclude(user=request.user)
            
            paginator = self.pagination_class()
            paginated_posts = paginator.paginate_queryset(Posts, request)
        
            if Posts!=None:
                serializer = PostSerializer(paginated_posts,many=True,context={"request":request})
                # print("Video_post:",serializer.data)
                return paginator.get_paginated_response(serializer.data)
            else:
                return Response({"details":"Loading....."})
        except Exception as error:
            print("Error:",error)
            return Response({"details":str(error)})
        

#search

class CombinedSearchView(APIView):
    permission_classes=[IsAuthenticated]
    
    def get(self, request):
        query = request.GET.get('query', '').strip()
        user = request.user

        # 1. Search users by username
        users = User.objects.filter(username__icontains=query,is_superuser=False,is_staff=False).select_related('profile')[:10]

        # 2. Search posts by caption or hashtags
        posts = Post.objects.filter(
            Q(caption__icontains=query) | Q(hashtags__name__icontains=query)
        ).select_related('user__profile').prefetch_related('hashtags').distinct()[:10]

        # 3. Serialize
        user_data = UserSearchSerializer(users, many=True).data
        post_data = PostSerializer(posts, many=True, context={'request': request}).data

        # 4. Return combined
        return Response({
            'users': user_data,
            'posts': post_data
        })

import os

def extract_cloudinary_public_id(url):
    
    try:
        parsed = urlparse(url)
        parts = parsed.path.strip('/').split('/')

        if 'upload' in parts:
            upload_index = parts.index('upload')
            # everything after 'upload/' is version and public_id
            public_id_with_ext = "/".join(parts[upload_index + 1:])  # v1751713680/filename.jpg
            filename = os.path.basename(public_id_with_ext)
            public_id = filename.rsplit('.', 1)[0]  # remove .jpg or .mp4
            print("Actual public_id sent to Cloudinary destroy:", public_id)

            return public_id
        return None
    except Exception as e:
        print("Error extracting public ID:", e)
        return None, None



# edit post
class PostEditView(APIView):
    permission_classes=[IsAuthenticated]
    def patch(self,request):
        try:
            user = request.user
            if user is not None:
                post_id=request.data.get('post_id')
                # post=Post.objects.get(id=post_id)

                if not post_id:
                    return Response({"error": "Post ID is required"}, status=400)

                try:
                    post = Post.objects.get(id=post_id, user=user)
                except Post.DoesNotExist:
                    return Response({"error": "Post not found or unauthorized"}, status=404)
                caption=request.data.get('description')
                media=request.FILES.get('media')

                old_url = post.media
                public_id =extract_cloudinary_public_id(old_url)
                
                if public_id:
                    destroy(public_id, resource_type=post.media_type)
                
                if media is not None:
                    upload_result = cloudinary.uploader.upload(media,resource_type='auto')
                    cloudinary_url = upload_result.get('secure_url')
                    post.media=cloudinary_url
                
                if caption is not None:
                    post.caption=caption
                    # print("Media:",media)

                # ✳️ Process comma-separated hashtag string
                
                raw_hashtags = request.data.get('query', '')
                if raw_hashtags is not None:
                    tag_names = [tag.strip().lstrip('#') for tag in raw_hashtags.split(',') if tag.strip()]
                    hashtag_objs = []
                    for name in tag_names:
                        tag, created = Hashtags.objects.get_or_create(name=name)
                        hashtag_objs.append(tag)
                    post.hashtags.set(hashtag_objs)
                post.save()

                return Response({"details": "Post updated Successfully...!"})
            else:
                return Response({"details": "Invalid user"}, status=401)

        except Exception as error:
            print("Error:", error)
            return Response({"error": str(error)}, status=500)

#delete post
class DeletePost(APIView):
    permission_classes=[IsAuthenticated]
    def delete(self,request,post_id):
        try:
            user = request.user
            post=Post.objects.get(id=post_id)
            
            # Step 1: Extract public ID from the Cloudinary URL
            media_url = post.media
            public_id = extract_cloudinary_public_id(media_url)

            print("URL:", media_url) # https://res.cloudinary.com/dq8biwq8q/image/upload/v1751713680/ib5lalz7td6pexlzjnkd.jpg
            print("Extracted public ID:", public_id)
            print("Resource type:", post.media_type)


            # Step 2: Delete media from Cloudinary (if it's not the default image)
            if public_id:
                result = destroy(public_id, resource_type=post.media_type)
                print("Cloudinary destroy result:", result)
            
            post.delete()
            return Response({"details":"Post deleted successfully...!"})
        except Exception as e:
            return Response({"details":str(e)})
        

# test cloud


class CloudinaryTestUpload(APIView):
    def get(self, request):
        try:
            # Upload a test image from the internet
            file_url = 'https://res.cloudinary.com/dq8biwq8q/image/upload/v1751525292/cld-sample-5.jpg'
            result = cloudinary.uploader.upload(file_url)
            return Response({
                'uploaded': True,
                'url': result.get('secure_url')
            })
        except Exception as e:
            return Response({'error': str(e)})