from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from notification_app.views import NotificatiinView,DeleteNotificationView,UnreadCoutView,MarkReadView


urlpatterns = [
    path('not/',NotificatiinView.as_view(),name='notifications'),
    path('delete-not/',DeleteNotificationView.as_view(),name='delete-not'),
    path('unread-count/',UnreadCoutView.as_view(),name='unread-count'),
    path('mark-read/',MarkReadView.as_view(),name='mark-read'),
]