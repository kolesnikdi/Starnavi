from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI
from users.views import users_router


api = NinjaAPI()
api.add_router("/users/", users_router)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls),
]
