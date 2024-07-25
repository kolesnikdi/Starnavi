from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.signals import user_logged_out
from django.db import IntegrityError

from ninja import Router

from api_posts_ai.authentication import create_token, AuthBearer
from users.schemas import UserCreateSuccessSchema, UserCreateSchema, ErrorSchema, UserLoginSchema, TokenSchema, \
    MessageSchema

users_router = Router()


@users_router.post('/register',  response={201: UserCreateSuccessSchema, 400: ErrorSchema})
def register(request, user: UserCreateSchema):
    try:
        user = User.objects.create(**user.dict())
        return 201, user
    except IntegrityError:
        return 400, {'error': 'Username or email already exists'}
    except Exception as e:
        return 400, {'error': str(e.args)}


@users_router.post("/login",  response={200: TokenSchema, 400: ErrorSchema})
def login(request, user: UserLoginSchema):
    user = authenticate(username=user.username, password=user.password.get_secret_value())
    if user is not None:
        token = create_token(user)
        return 200, {"token": token}
    return 400, {"error": "Invalid credentials"}


@users_router.post('/logout', auth=AuthBearer(), response={200: MessageSchema, })
def logout(request):
    user = request.auth
    user_logged_out.send(sender=user.__class__, request=request, user=user)
    return 200, {"message": "Successfully logged out"}
