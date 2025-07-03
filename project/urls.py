from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),

    # user_app
    path('api/user/',include('Apps.user_app.urls')),
    
    #post_app
    path('api/post/',include('Apps.post_app.urls')),

    #notification_app
    path('api/notification/',include('Apps.notification_app.urls')),

    #interaction_app
    path('api/interaction/',include('Apps.interaction_app.urls')),

    #mesage_app
    path('api/messenger/',include('Apps.message_app.urls'))
]

# if settings.DEBUG:
#     urlpatterns+= static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
