from django.urls import path

from users.api import login, logout, logout_all

urlpatterns = [
    path('login/', login, name='knox_login'),
    path('logout/', logout, name='knox_logout'),
    path('logoutall/', logout_all, name='knox_logoutall'),
]
