import pytest
import random
import string
from ninja.testing import TestClient

from api_posts_ai.urls import api

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
def api_client():
    client = TestClient()
    return client
