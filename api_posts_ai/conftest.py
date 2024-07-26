from django.conf import settings

import pytest
import random
import string
import jwt
from datetime import datetime, timedelta

from ninja.testing import TestClient


"""randomizers"""


@pytest.fixture(scope='function')
def randomizer():
    return Randomizer()


class Randomizer:

    def email(self):
        """ randomize data for email"""
        return ''.join(random.choice(string.hexdigits) for i in range(10)) + "@gmail.com"

    def upp2_data(self):
        """ randomize data for password"""
        return ''.join(random.choice(string.hexdigits) for i in range(10))

    def random_name(self):
        """ randomize data for username"""
        return ''.join(random.choice(string.ascii_letters) for i in range(10)).title()

    def random_name_limit(self, limit):
        """ randomize data for username"""
        return ''.join(random.choice(string.ascii_letters) for i in range(limit)).title()

    def user(self):
        """ randomize data user"""
        user = {
            'username': ''.join(random.choice(string.ascii_letters) for i in range(10)).title(),
            'password': ''.join(random.choice(string.hexdigits) for i in range(10)),
            'email': ''.join(random.choice(string.hexdigits) for i in range(10)) + "@gmail.com",
        }
        return user


"""created custom users"""


@pytest.fixture
def api_client(request):
    return TestClient(request.param)


@pytest.fixture(scope='function')
def user(django_user_model, randomizer):
    data = randomizer.user()
    user = django_user_model.objects.create_user(**data)
    user.user_password = data['password']
    return user


@pytest.fixture
def auth_user(api_client, user, ):
    from django.contrib.auth import authenticate
    user = authenticate(username=user.username, password=user.user_password)
    api_client.token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(seconds=60),
        'iat': datetime.utcnow()
    }, settings.SECRET_KEY, algorithm='HS256')
    api_client.user = user
    api_client.headers = {"Authorization": f"Bearer {api_client.token}"}
    return api_client
