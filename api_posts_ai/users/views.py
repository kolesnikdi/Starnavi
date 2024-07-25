from django.contrib.auth.models import User
from django.db import IntegrityError

from ninja import Router

from users.schemas import UserCreateSuccessSchema, UserCreateSchema, ErrorSchema

users_router = Router()

@users_router.post('/register',  response={201: UserCreateSuccessSchema, 400: ErrorSchema})
def register(request, user: UserCreateSchema):
    try:
        user = User.objects.create(**user.dict())
        return 201, user
    except IntegrityError:
        return 400, {'message': 'Username or email already exists'}
    except Exception as e:
        return 400, {'message': str(e.args)}
