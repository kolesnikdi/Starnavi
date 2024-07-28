from django.conf import settings
from django.contrib.auth.models import User

import jwt
import pytest

from api_posts_ai.authentication import create_token
from users.views import users_router


@pytest.mark.parametrize('api_client', [users_router], indirect=True)
class TestUsers:

    @pytest.mark.django_db
    def test_register_success(self, api_client, randomizer):
        data = randomizer.user()
        response = api_client.post('/register', json={**data})
        assert response.status_code == 201
        response_json = response.json()
        assert response_json['id'] == User.objects.get(username=data['username']).id
        assert response_json['username'] == data['username']
        assert response_json['email'] == data['email']

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
        response_json = response.json()
        assert response_json['detail'][0]['msg'] == 'String should have at least 3 characters'
        assert response_json['detail'][1]['msg'] == 'String should have at least 8 characters'
        assert response_json['detail'][2][
                   'msg'] == 'value is not a valid email address: An email address must have an @-sign.'


@pytest.mark.parametrize('api_client', [users_router], indirect=True)
class TestLoginLogout:

    @pytest.mark.django_db
    def test_login_success(self, api_client, user, randomizer):
        response = api_client.post('/login', json={"username": user.username, "password": user.user_password})
        assert response.status_code == 200
        response_json = response.json()
        assert "token" in response_json
        payload = jwt.decode(response_json['token'], settings.SECRET_KEY, algorithms=['HS256'])
        assert payload['user_id'] == user.id

    @pytest.mark.django_db
    def test_login_failure(self, api_client, user, randomizer):
        response = api_client.post('/login', json={"username": user.username, "password": 'user.user_password'})
        assert response.status_code == 400
        assert response.json() == {'error': 'Invalid credentials'}

    @pytest.mark.django_db
    def test_renew_token_success(self, api_client, user):
        token = create_token(user)
        response = api_client.post('/renew_token', headers={'Authorization': f'Bearer {token}'})
        assert response.status_code == 200
        response_json = response.json()
        assert "token" in response_json
        payload = jwt.decode(response_json['token'], settings.SECRET_KEY, algorithms=['HS256'])
        assert payload['user_id'] == user.id

    @pytest.mark.django_db
    def test_renew_token_without_token(self, api_client):
        response = api_client.post('/renew_token')
        assert response.status_code == 401
        assert response.json() == {'detail': 'Unauthorized'}

    @pytest.mark.django_db
    def test_renew_token_with_invalid_token(self, api_client):
        headers = {'Authorization': 'Bearer invalidtoken'}
        response = api_client.post('/renew_token', headers=headers)
        assert response.status_code == 401
        assert response.json() == {'detail': 'Unauthorized'}

    @pytest.mark.django_db
    def test_renew_token_user_delete(self, api_client, user):
        token = create_token(user)
        user.delete()
        response = api_client.post('/renew_token', headers={'Authorization': f'Bearer {token}'})
        assert response.status_code == 401
        assert response.json() == {'detail': 'Unauthorized'}
