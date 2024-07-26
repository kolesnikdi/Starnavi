from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI

from posts_comments.views import post_router
from users.views import users_router


api = NinjaAPI()
api.add_router("/users/", users_router)
api.add_router("/post/", post_router)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls),
]
