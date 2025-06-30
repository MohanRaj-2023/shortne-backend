# from django.contrib import admin
from django.urls import path
from .views import HashtagSearchView,PostCreateView,PostsView,PostView,GetPosts,VideoPostsView,CombinedSearchView,PostEditView,DeletePost
# PostCreateView

urlpatterns=[
    path('home/',GetPosts.as_view(),name='get-post'),
    path('hashtags/search/',HashtagSearchView.as_view(),name='hashtags-search'),
    path('post-create/',PostCreateView.as_view(),name='post-save'),
    path('posts/',PostsView.as_view(),name="post's-view"),
    path('post-view/<int:post_id>/',PostView.as_view(),name='post-view'),
    path('videos/',VideoPostsView.as_view(),name='video-post'),
    path('search/',CombinedSearchView.as_view(),name='search'),
    path('post-edit/',PostEditView.as_view(),name='post-edit'),
    path('post-delete/<int:post_id>/',DeletePost.as_view(),name='post-delete'),
    ]