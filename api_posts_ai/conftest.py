import pytest
import random
import string
from datetime import datetime, timedelta

from ninja.testing import TestClient

from posts_comments.models import Post, PostSettings

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


@pytest.fixture(scope='function')
def user_2(django_user_model, randomizer):
    data = randomizer.user()
    user_2 = django_user_model.objects.create_user(**data)
    user_2.user_password = data['password']
    return user_2


@pytest.fixture(scope='function')
def new_post(user, randomizer):
    post = Post.add_root(user_id=user.id, text=randomizer.random_name_limit(50))
    PostSettings.objects.create(post=post, is_ai_reply=True)
    return post


@pytest.fixture(scope='function')
def new_post_2(user_2, randomizer):
    post = Post.add_root(user_id=user_2.id, text=randomizer.random_name_limit(50))
    PostSettings.objects.create(post=post, is_ai_reply=True)
    return post


def add_comments(post, user, user_2, randomizer, created_date, depth):
    if depth > 0:
        if not post.is_blocked:
            comment_1 = post.add_child(user_id=user.id if depth % 2 else user_2.id,
                                       text=randomizer.random_name_limit(50),
                                       is_blocked=False)
            comment_2 = post.add_child(user_id=user.id if depth % 2 else user_2.id,
                                       text=randomizer.random_name_limit(50),
                                       is_blocked=True)
            add_comments(comment_1, user, user_2, randomizer, created_date, depth - 1)
            add_comments(comment_2, user, user_2, randomizer, created_date, depth - 1)
        else:
            return
    return Post.objects.all().filter(path__startswith=post.path, depth__gte=post.depth)


@pytest.fixture(scope='function')
def daily_breakdown_data(new_post_2, new_post, user, user_2, randomizer):
    created_date = datetime.now()
    second_date = created_date - timedelta(days=1)
    third_date = created_date - timedelta(days=4)
    third = add_comments(new_post, user, user_2, randomizer, third_date, depth=3)
    third.update(created_date=third_date)
    second = add_comments(new_post_2, user_2, user, randomizer, second_date, depth=4)
    second.update(created_date=second_date)
    first = add_comments(new_post, user, user_2, randomizer, created_date, depth=5)
    daily_breakdown_data = Post.objects.all()
    daily_breakdown_data.date_to = created_date.strftime('%Y-%m-%d')
    daily_breakdown_data.date_from = third_date.strftime('%Y-%m-%d')

    return daily_breakdown_data


@pytest.fixture(scope='function')
def post_comments(randomizer, new_post, user, user_2):
    created_date = datetime.now()
    add_comments(new_post, user, user_2, randomizer, created_date, depth=3)

    return Post.objects.all()
