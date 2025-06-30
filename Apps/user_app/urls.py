from django.contrib import admin
from django.urls import path
from .views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('signup/', SignupView.as_view(),name='signup'),
    path('signin/',SigninView.as_view(),name='signin'),
    path('signout/',SignoutView.as_view(),name='signout'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('activate/<uidb64>/<token>',ActivateView.as_view(),name='activate'),
    # path('user/',UserProfile.as_view(),name='userprofile'),
    path('accounts/password/reset/',PasswordupdaterequestView.as_view(),name='resetpasswordemail'),
    path('accounts/password/reset/confirm/',ResetPasswordView.as_view(),name='resetpassword'),
    path('user-profile/',UserProfileView.as_view(),name='userprofile'),
    path('follow/',FollowView.as_view(),name='follow'),
    path('unfollow/',UnfollowView.as_view(),name='unfollow'),
    path('follow/status/',FollowStatusView.as_view(),name='follow-status'),
    path('followers/',FollowersView.as_view(),name='followers'),
    path('friends/',FriendslistView.as_view(),name='friends'),
    path('user-profile/edit/',EditUserinfoView.as_view(),name='edit-profile'),
]