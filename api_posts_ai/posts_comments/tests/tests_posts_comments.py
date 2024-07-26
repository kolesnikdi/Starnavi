from django.conf import settings
from django.contrib.auth.models import User

import jwt
import pytest
from datetime import datetime

from posts_comments.models import Post
from posts_comments.views import post_router


@pytest.mark.parametrize('api_client', [post_router], indirect=True)
class TestPostsComments:

    @pytest.mark.django_db
    def test_create_post_success(self, auth_user, randomizer):
        text = randomizer.random_name_limit(50)
        response = auth_user.post('/create', json={'text': text})
        assert response.status_code == 201
        assert response.json()['id'] == Post.objects.get(user_id=auth_user.user.id).id
        assert response.json()['user_id'] == auth_user.user.id
        assert response.json()['text'] == text
        assert isinstance(response.json()['created_date'], datetime)

    @pytest.mark.django_db
    def test_register_username_exists(self, api_client, randomizer):
        data = randomizer.user()
        User.objects.create_user(**data)
        response = api_client.post('/register', json={**data})
        assert response.status_code == 400
        assert response.json() == {'error': 'Username or email already exists'}

    @pytest.mark.django_db
    def test_register_invalid_data(self, api_client):
        response = api_client.post('/register', json={
            'username': 'us',
            'password': 'pwd',
            'email': 'invalidemail'
        })
        assert response.status_code == 422
        assert response.json()['detail'][0]['msg'] == 'String should have at least 3 characters'
        assert response.json()['detail'][1]['msg'] == 'String should have at least 8 characters'
        assert response.json()['detail'][2][
                   'msg'] == 'value is not a valid email address: An email address must have an @-sign.'


class TestLoginLogout:

    @pytest.mark.django_db
    def test_login_success(self, api_client, user, randomizer):
        response = api_client.post('/login', json={"username": user.username, "password": user.user_password})
        assert response.status_code == 200
        assert "token" in response.json()
        payload = jwt.decode(response.json()['token'], settings.SECRET_KEY, algorithms=['HS256'])
        assert payload['user_id'] == user.id

    @pytest.mark.django_db
    def test_login_failure(self, api_client, user, randomizer):
        response = api_client.post('/login', json={"username": user.username, "password": 'user.user_password'})
        assert response.status_code == 400
        assert response.json() == {'error': 'Invalid credentials'}

    @pytest.mark.django_db
    def test_renew_token_success(self, auth_user):
        response = auth_user.post('/renew_token', headers=auth_user.headers)
        assert response.status_code == 200
        assert "token" in response.json()
        payload = jwt.decode(response.json()['token'], settings.SECRET_KEY, algorithms=['HS256'])
        assert payload['user_id'] == auth_user.user.id

    @pytest.mark.django_db
    def test_renew_token_without_token(self, api_client):
        response = api_client.post('/renew_token')
        assert response.status_code == 401
        assert response.json() == {'detail': 'Unauthorized'}

    @pytest.mark.django_db
    def test_renew_token_with_invalid_token(self, api_client):
        headers = {"Authorization": "Bearer invalidtoken"}
        response = api_client.post('/renew_token', headers=headers)
        assert response.status_code == 401
        assert response.json() == {'detail': 'Unauthorized'}

    @pytest.mark.django_db
    def test_renew_token_user_delete(self, auth_user, api_client):
        headers = auth_user.headers
        auth_user.user.delete()
        response = api_client.post('/renew_token', headers=headers)
        assert response.status_code == 401
        assert response.json() == {'detail': 'Unauthorized'}
