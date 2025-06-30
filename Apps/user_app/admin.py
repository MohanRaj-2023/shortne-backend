from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from user_app.models import User,UserProfile,Follow
# Register your models here.

admin.site.register(User,UserAdmin)
admin.site.register(UserProfile)
admin.site.register(Follow)