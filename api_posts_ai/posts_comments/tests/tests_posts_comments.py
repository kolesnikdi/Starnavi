import pytest

from api_posts_ai.authentication import create_token
from posts_comments.models import Post
from posts_comments.views import post_router


@pytest.mark.parametrize('api_client', [post_router], indirect=True)
class TestPostsComments:

    @pytest.mark.django_db
    def test_create_post_success(self, api_client, randomizer, user):
        text = randomizer.random_name_limit(50)
        token = create_token(user)
        response = api_client.post('/', json={'text': text}, headers={'Authorization': f'Bearer {token}'})
        assert response.status_code == 201
        response_json = response.json()
        assert response_json['id'] == Post.objects.get(user_id=user.id).id
        assert response_json['user_id'] == user.id
        assert response_json['text'] == text
        assert response_json['created_date']

    @pytest.mark.django_db
    def test_create_post_valid_text(self, api_client, randomizer, user):
        pass

    @pytest.mark.django_db
    def test_create_post_invalid_text(self, api_client, randomizer, user):
        pass

    @pytest.mark.django_db
    def test_create_comment_success(self, api_client, randomizer, user, new_post):
        text = randomizer.random_name_limit(50)
        token = create_token(user)
        response = api_client.post(f'/{new_post.id}', json={'text': text}, headers={'Authorization': f'Bearer {token}'})
        assert response.status_code == 201
        response_json = response.json()
        assert response_json['id'] == Post.objects.filter(user_id=user.id).last().id
        assert response_json['user_id'] == user.id
        assert response_json['text'] == text
        assert response_json['created_date']

    @pytest.mark.django_db
    def test_create_comment_invalid_post(self, api_client, randomizer, user, new_post):
        text = randomizer.random_name_limit(50)
        token = create_token(user)
        response = api_client.post('/2', json={'text': text}, headers={'Authorization': f'Bearer {token}'})
        assert response.status_code == 404
        response_json = response.json()
        assert response_json['detail'] == 'Not Found'

    @pytest.mark.django_db
    def test_update_post_comment_success(self, api_client, randomizer, user, new_post):
        old_text = new_post.text
        text = randomizer.random_name_limit(50)
        token = create_token(user)
        response = api_client.patch(f'/{new_post.id}', json={'text': text}, headers={'Authorization': f'Bearer {token}'})
        assert response.status_code == 200
        response_json = response.json()
        assert response_json['id'] == Post.objects.filter(user_id=user.id).last().id
        assert response_json['user_id'] == user.id
        assert response_json['text'] != old_text
        assert response_json['text'] == text
        assert response_json['created_date']

    @pytest.mark.django_db
    def test_update_post_comment_not_owner(self, api_client, randomizer, user_2, new_post):
        text = randomizer.random_name_limit(50)
        token = create_token(user_2)
        response = api_client.patch(f'/{new_post.id}', json={'text': text}, headers={'Authorization': f'Bearer {token}'})
        assert response.status_code == 405
        response_json = response.json()
        assert response_json['error'] == 'This action is allowed only to the owner'

    @pytest.mark.django_db
    def test_delete_post_comment_success(self, api_client, randomizer, user, new_post):
        token = create_token(user)
        response = api_client.delete(f'/{new_post.id}', headers={'Authorization': f'Bearer {token}'})
        assert response.status_code == 204
        response_json = response.json()
        assert response_json['detail'] == 'It was deleted successfully'

    @pytest.mark.django_db
    def test_delete_post_comment_not_owner(self, api_client, randomizer, user_2, new_post):
        token = create_token(user_2)
        response = api_client.delete(f'/{new_post.id}', headers={'Authorization': f'Bearer {token}'})
        assert response.status_code == 405
        response_json = response.json()
        assert response_json['error'] == 'This action is allowed only to the owner'

    @pytest.mark.django_db
    def test_delete_post_comment_has_reply(self, api_client, randomizer, user, new_post):
        text = randomizer.random_name_limit(50)
        token = create_token(user)
        response = api_client.post(f'/{new_post.id}', json={'text': text}, headers={'Authorization': f'Bearer {token}'})
        assert response.status_code == 201
        response = api_client.delete(f'/{new_post.id}', headers={'Authorization': f'Bearer {token}'})
        assert response.status_code == 405
        response_json = response.json()
        assert response_json['error'] == 'You cannot delete a post with comments to it'


    @pytest.mark.django_db
    def test_get_post_comment_success(self, api_client, post_comments):
        token = create_token(post_comments[0].user)
        response = api_client.get(f'/{post_comments[0].id}', headers={'Authorization': f'Bearer {token}'})
        assert response.status_code == 200
        response_json = response.json()
        assert response_json['id'] == post_comments[0].id
        assert response_json['text'] == post_comments[0].text
        assert response_json['created_date']
        assert response_json['user_id'] == post_comments[0].user.id
        assert len(response_json['descendants']) == len(post_comments) - 1
        assert len(response_json['descendants'][0]['descendants'][0]['descendants']) == 2
        assert response_json['descendants'][0]['descendants'][0]['descendants'][0]['descendants'] == []
