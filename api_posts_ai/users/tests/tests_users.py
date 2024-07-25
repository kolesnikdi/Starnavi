import pytest

from django.contrib.auth.models import User


class TestUsers:

    @pytest.mark.django_db
    def test_register_success(self, api_client, randomizer):
        data = randomizer.user()
        response = api_client.post('/api/users/register', json={**data})
        assert response.status_code == 201
        assert response.json()['id'] == User.objects.get(username=data['username']).id
        assert response.json()['username'] == data['username']
        assert response.json()['email'] == data['email']

    @pytest.mark.django_db
    def test_register_username_exists(self, api_client, randomizer):
        data = randomizer.user()
        User.objects.create_user(++data)
        response = api_client.post('/api/users/register', json={**data})
        assert response.status_code == 400
        assert response.json() == {'message': 'Username or email already exists'}


    @pytest.mark.django_db
    def test_register_invalid_data(self, api_client):
        response = api_client.post('/api/users/register', json={
            "username": "us",
            "password": "pwd",
            "email": "invalidemail"
        })
        assert response.status_code == 400
        assert "message" in response.json()