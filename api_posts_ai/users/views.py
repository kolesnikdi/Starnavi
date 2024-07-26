from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db import IntegrityError

from ninja import Router

from api_posts_ai.authentication import create_token, AuthBearer
from users.schemas import UserCreateSuccessSchema, UserCreateSchema, ErrorSchema, UserLoginSchema, TokenSchema

users_router = Router()


@users_router.post('/register', response={201: UserCreateSuccessSchema, 400: ErrorSchema})
def register(request, user: UserCreateSchema):
    try:
        user = User.objects.create(**user.dict())
        return 201, user
    except IntegrityError:
        return 400, {'error': 'Username or email already exists'}
    except Exception as e:
        return 400, {'error': str(e.args)}


@users_router.post("/login", response={200: TokenSchema, 400: ErrorSchema})
def login(request, user: UserLoginSchema):
    user = authenticate(username=user.username, password=user.password.get_secret_value())
    if user is not None:
        token = create_token(user)
        return 200, {'token': token}
    return 400, {'error': 'Invalid credentials'}


@users_router.post('/renew_token', auth=AuthBearer(), response={200: TokenSchema})
def renew_token(request):
    user = request.auth
    token = create_token(user)
    return 200, {'token': token}
