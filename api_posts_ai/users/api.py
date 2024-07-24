from django.contrib.auth import authenticate
from django.contrib.auth.signals import user_logged_out
from django.contrib.auth.models import User

from ninja.responses import Response
from knox.models import AuthToken
from rest_framework.exceptions import AuthenticationFailed

from api_posts_ai.authentication import KnoxAuth
from api_posts_ai.urls import users_api
from users.schemas import UserLoginSchema, UserCreateSchema


@users_api.post('/login')
def login(request, user: UserLoginSchema):
    user = authenticate(username=user.username, password=user.password)
    if user is None:
        raise AuthenticationFailed('Invalid credentials')
    _, token = AuthToken.objects.create(user)
    return Response({'token': token}, status=200)


@users_api.post('/logout', auth=KnoxAuth())
def logout(request):
    request._auth.delete()
    user_logged_out.send(sender=request.user.__class__,
                         request=request, user=request.user)
    return Response({'message': 'Logged out successfully'}, status=204)


@users_api.post('/logout', auth=KnoxAuth())
def logout_all(request):
    request.user.auth_token_set.all().delete()
    user_logged_out.send(sender=request.user.__class__,
                         request=request, user=request.user)
    return Response({'message': 'Logged out of all sessions'}, status=204)


@users_api.post('/register')
def register(request, user: UserCreateSchema,  response=UserCreateSchema):
    if User.objects.filter(username=user.username).exists():
        return Response({'error': 'Username already exists'}, status=400)
    try:
        user = User.objects.create(**user.dict())
        return Response(user, status=200)
    except Exception as e:
        return Response({'error': f'{e}'}, status=400)
