from django.contrib import admin
from interaction_app.models import Comment,PostLikeDislike,CommentLikeDislike

# Register your models here.
admin.site.register(Comment)

admin.site.register(PostLikeDislike)

admin.site.register(CommentLikeDislike)

# admin.site.register(SharePost)