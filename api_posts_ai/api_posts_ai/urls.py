from django.contrib import admin
from django.urls import path, include
from ninja import NinjaAPI


users_api = NinjaAPI()

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', users_api.urls),
    path('', include('users.urls')),
]
