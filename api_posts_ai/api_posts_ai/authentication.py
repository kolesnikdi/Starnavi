from django.contrib.auth.models import User
from django.conf import settings

from ninja.security import HttpBearer
import jwt
from datetime import datetime

from api_posts_ai.settings import JWT_TTL


def create_token(user):
    payload = {
        'user_id': user.id,
        'exp': datetime.utcnow() + JWT_TTL,
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')


class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload['user_id']
            user = User.objects.get(id=user_id)
            return user
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
        except User.DoesNotExist:
            return None
