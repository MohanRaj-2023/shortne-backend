from django.contrib import admin
from django.urls import path
from interaction_app.views import (CreateCommentView,EditCommentView,CommentView,DeleteCommentView,
                                   Post_Like_Dislike_View,Comment_Like_Dislike_View)

urlpatterns = [
    path('comment/',CreateCommentView.as_view(),name='comment'),
    path('comment-edit/',EditCommentView.as_view(),name='comment-edit'),
    path('comment-view/',CommentView.as_view(),name='comment-view'),
    path('comment-delete/',DeleteCommentView.as_view(),name='comment-delete'),
    path('post-react/',Post_Like_Dislike_View.as_view(),name='post-react'),
    path('comment-react/',Comment_Like_Dislike_View.as_view(),name='comment-react'),
    # path('share-post/',SharePostView.as_view(),name='share-post'),
]