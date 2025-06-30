from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from interaction_app.models import Comment,PostLikeDislike,CommentLikeDislike
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from post_app.models import Post
from user_app.models import User

# serializer
from interaction_app.serializers import CommentSerializer

# message modal
from message_app.models import Message

# Create your views here.

# Create Comment View
class CreateCommentView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            comment = request.data.get('comment')
            post    = request.data.get('postid')
            user    = request.user
            post_inst = Post.objects.get(id=post)
            print("Post:",Post)
            comment_inst=Comment.objects.create(comment=comment,post=post_inst,user=user)
            serializer = CommentSerializer(comment_inst,context={"request":request})
            print("Created_Commant:",serializer.data)
            return Response({"details":"Comment created successfully...!",
                             "comment":serializer.data})
        except Exception as error:
            return {"details":str(error)}

        
# Edit Comment
class EditCommentView(APIView):
    permission_classes = [IsAuthenticated]
    def patch(self,request):
        # comment = request.query_params.get('comment')
        # comment_id = request.query_params.get('id')
        try:
            comment_text = request.data.get('comment')
            comment_id = request.data.get('id')
            print("Comment_id:",comment_id)
            comment_inst = Comment.objects.filter(id=comment_id).first()

            if not comment_inst:
                return Response({"details": "Comment not found."}, status=status.HTTP_404_NOT_FOUND)

            if comment_inst.user != request.user:
                return Response({"details": "You are not authorized to edit this comment."}, status=status.HTTP_403_FORBIDDEN)

            comment_inst.comment=comment_text
            comment_inst.save()
            serializer = CommentSerializer(comment_inst,context={"request":request})
            try:
                print("Comment_instance:", serializer.data)
            except Exception as log_error:
                print("Logging error:", log_error)

            print("Comment_intsance:",serializer.data)
            return Response({"details":"Comment edited successfully...!",
                             "comment":serializer.data})
        except Exception as error:
            print("Edit Error:",error)
            return Response({"details":str(error)})
        
# delete Comment 
class DeleteCommentView(APIView):
    permission_classes=[IsAuthenticated]
    def delete(self,request):
        try:
            comment_id = request.query_params.get('id')
            comment=Comment.objects.get(id=comment_id)
            comment.delete()
            print("Deleted_id:",comment_id)
            print("Comment deleted successfully")
            return Response({"details":"Comment deleted successfully...!",
                             "comment_id":comment_id})
        except Exception as error:
            return Response({"details":str(error)})

# Get Comments
class CommentView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            post_id = request.query_params.get('postid')
            print("POST_ID:",post_id)
            post_instance = Post.objects.get(id=post_id)
            comments = Comment.objects.filter(post=post_instance)
            serializer = CommentSerializer(comments,many=True,context={"request":request})
            return Response({"details":serializer.data})
        except Exception as error:
            print("Error:",error)
            return Response({"details":str(error)})
        

# Post Like Dislike
class Post_Like_Dislike_View(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        user = request.user
        post_id = request.data.get('post_id')
        is_like = request.data.get('is_like')
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
             return Response({"details":"Not post found in that id"})
        try:
            like_inst = PostLikeDislike.objects.get(user=user,post=post)
            if like_inst.is_like == is_like:
                        like_inst.delete()
                        return Response({"details":"Reaction removed"})
            else:
                        like_inst.is_like=is_like
                        like_inst.save()
                        return Response({"details":"Reaction updated"})    
        except PostLikeDislike.DoesNotExist:
            PostLikeDislike.objects.create(user=user,post=post,is_like=is_like)
            return Response({"details":"Reaction Created"})

# Comment Like Dislike
class Comment_Like_Dislike_View(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        user = request.user
        comment_id = request.data.get('comment_id')
        is_like = request.data.get('is_like')
        try:
            comment = Comment.objects.get(id=comment_id)
        except Post.DoesNotExist:
             return Response({"details":"Not post found in that id"})
        try:
            like_inst = CommentLikeDislike.objects.get(user=user,comment=comment)
            if like_inst.is_like == is_like:
                        like_inst.delete()
                        return Response({"details":"Reaction removed"})
            else:
                        like_inst.is_like=is_like
                        like_inst.save()
                        return Response({"details":"Reaction updated"})    
        except CommentLikeDislike.DoesNotExist:
            CommentLikeDislike.objects.create(user=user,comment=comment,is_like=is_like)
            return Response({"details":"Reaction Created"})
        
