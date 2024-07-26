import pytest
import random
import string

from ninja.testing import TestClient

from posts_comments.models import Post

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
    return post


@pytest.fixture(scope='function')
def post_comments(randomizer, new_post, user, user_2):
    def add_comments(post, depth):
        if depth > 0:
            comment_1 = post.add_child(user_id=user.id if depth % 2 else user_2.id,
                                           text=randomizer.random_name_limit(50))
            comment_2 = post.add_child(user_id=user.id if depth % 2 else user_2.id,
                                           text=randomizer.random_name_limit(50))
            add_comments(comment_1, depth - 1)
            add_comments(comment_2, depth - 1)

    add_comments(new_post, 3)

    return Post.objects.all()
