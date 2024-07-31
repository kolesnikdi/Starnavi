import pytest
from datetime import datetime, timedelta

from api_posts_ai.authentication import create_token
from api_posts_ai.constants import ReplyDialogue
from posts_comments.models import Post
from posts_comments.views import post_router


@pytest.mark.parametrize('api_client', [post_router], indirect=True)
class TestPostsComments:

    @pytest.mark.django_db
    def test_create_post_valid_text_success(self, api_client, randomizer, user):
        text = randomizer.random_name_limit(50)
        token = create_token(user)
        response = api_client.post('/', json={'text': text}, headers={'Authorization': f'Bearer {token}'})
        assert response.status_code == 201
        response_json = response.json()
        post = Post.objects.get(user_id=user.id)
        assert response_json['id'] == post.id
        assert response_json['user_id'] == user.id
        assert response_json['text'] == text
        assert response_json['is_blocked'] == post.is_blocked
        assert response_json['is_blocked'] is False
        assert response_json['created_date']
        post_settings = post.settings.get()
        assert post_settings.is_ai_reply is False
        assert post_settings.time_sleep == 0
        assert post_settings.creativity == 0.5
        assert post_settings.reply_or_dialogue == ReplyDialogue.REPLY
        assert post_settings.base_reply == 'I\'m not available right now. I will answer later'

    @pytest.mark.django_db
    def test_create_post_invalid_text(self, api_client, randomizer, user):
        text = randomizer.random_name_limit(50) + ' dick, slut, хуй'
        token = create_token(user)
        response = api_client.post('/', json={'text': text}, headers={'Authorization': f'Bearer {token}'})
        assert response.status_code == 201
        response_json = response.json()
        post = Post.objects.get(user_id=user.id)
        assert response_json['id'] == post.id
        assert response_json['user_id'] == user.id
        assert response_json['text'] == text
        assert response_json['is_blocked'] == post.is_blocked
        assert response_json['is_blocked'] is True
        assert response_json['created_date']
        post_settings = post.settings.get()
        assert post_settings.is_ai_reply is False
        assert post_settings.time_sleep == 0
        assert post_settings.creativity == 0.5
        assert post_settings.reply_or_dialogue == ReplyDialogue.REPLY
        assert post_settings.base_reply == 'I\'m not available right now. I will answer later'

    @pytest.mark.django_db
    def test_create_comment_valid_text_success_one_reply(self, api_client, randomizer, user_2, new_post):
        text = randomizer.random_name_limit(50)
        token = create_token(user_2)
        response = api_client.post(f'/{new_post.id}', json={'text': text}, headers={'Authorization': f'Bearer {token}'})
        assert response.status_code == 201
        response_json = response.json()
        comment = Post.objects.filter(user_id=user_2.id).last()
        assert response_json['id'] == comment.id
        assert response_json['user_id'] == user_2.id
        assert response_json['text'] == text
        assert response_json['created_date']
        assert response_json['is_blocked'] == comment.is_blocked
        assert response_json['is_blocked'] is False
        reply = comment.get_descendants().first()
        assert reply.user.id == new_post.user.id
        assert reply.is_ai_comment is True
        assert reply.text
        assert reply.is_blocked is False
        text_2 = randomizer.random_name_limit(50)
        response_2 = api_client.post(f'/{reply.id}', json={'text': text_2},
                                     headers={'Authorization': f'Bearer {token}'})
        assert response_2.status_code == 201
        comment_2 = Post.objects.filter(user_id=user_2.id).last()
        reply_2 = comment_2.get_descendants().first()
        assert reply_2 is None

    @pytest.mark.django_db
    def test_create_comment_valid_text_success_no_reply(self, api_client, randomizer, user_2, new_post):
        text = randomizer.random_name_limit(50)
        token = create_token(user_2)
        new_post_settings = new_post.settings.get()
        new_post_settings.is_ai_reply = False
        new_post_settings.save()
        response = api_client.post(f'/{new_post.id}', json={'text': text}, headers={'Authorization': f'Bearer {token}'})
        assert response.status_code == 201
        response_json = response.json()
        comment = Post.objects.filter(user_id=user_2.id).last()
        assert response_json['id'] == comment.id
        assert response_json['user_id'] == user_2.id
        assert response_json['text'] == text
        assert response_json['created_date']
        assert response_json['is_blocked'] == comment.is_blocked
        assert response_json['is_blocked'] is False
        reply = comment.get_descendants().first()
        assert reply is None

    @pytest.mark.django_db
    def test_create_comment_valid_text_success_dialogue(self, api_client, randomizer, user_2, new_post):
        text = randomizer.random_name_limit(50)
        token = create_token(user_2)
        new_post_settings = new_post.settings.get()
        new_post_settings.reply_or_dialogue = ReplyDialogue.DIALOGUE
        new_post_settings.save()
        response = api_client.post(f'/{new_post.id}', json={'text': text}, headers={'Authorization': f'Bearer {token}'})
        assert response.status_code == 201
        response_json = response.json()
        comment = Post.objects.filter(user_id=user_2.id).last()
        assert response_json['id'] == comment.id
        assert response_json['user_id'] == user_2.id
        assert response_json['text'] == text
        assert response_json['created_date']
        assert response_json['is_blocked'] == comment.is_blocked
        assert response_json['is_blocked'] is False
        reply = comment.get_descendants().first()
        assert reply.user.id == new_post.user.id
        assert reply.is_ai_comment is True
        assert reply.text
        assert reply.is_blocked is False
        text_2 = randomizer.random_name_limit(50)
        response_2 = api_client.post(f'/{reply.id}', json={'text': text_2},
                                     headers={'Authorization': f'Bearer {token}'})
        assert response_2.status_code == 201
        comment_2 = Post.objects.filter(user_id=user_2.id).last()
        reply_2 = comment_2.get_descendants().first()
        assert reply_2.user.id == new_post.user.id
        assert reply_2.is_ai_comment is True
        assert reply_2.text
        assert reply_2.is_blocked is False

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
        response = api_client.patch(f'/{new_post.id}', json={'text': text},
                                    headers={'Authorization': f'Bearer {token}'})
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
        response = api_client.patch(f'/{new_post.id}', json={'text': text},
                                    headers={'Authorization': f'Bearer {token}'})
        assert response.status_code == 404
        response_json = response.json()
        assert response_json['detail'] == 'Not Found'

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
        assert response.status_code == 404
        response_json = response.json()
        assert response_json['detail'] == 'Not Found'

    @pytest.mark.django_db
    def test_delete_post_comment_has_reply(self, api_client, randomizer, user, new_post):
        text = randomizer.random_name_limit(50)
        token = create_token(user)
        response = api_client.post(f'/{new_post.id}', json={'text': text}, headers={'Authorization': f'Bearer {token}'})
        assert response.status_code == 201
        response = api_client.delete(f'/{new_post.id}', headers={'Authorization': f'Bearer {token}'})
        assert response.status_code == 403
        response_json = response.json()
        assert response_json['error'] == 'You cannot delete a post with comments to it'

    @pytest.mark.django_db
    def test_get_post_comments_success(self, api_client, post_comments):
        token = create_token(post_comments[0].user)
        response = api_client.get(f'/{post_comments[0].id}', headers={'Authorization': f'Bearer {token}'})
        assert response.status_code == 200
        response_json = response.json()
        assert response_json['id'] == post_comments[0].id
        assert response_json['text'] == post_comments[0].text
        assert response_json['created_date']
        assert response_json['user_id'] == post_comments[0].user.id
        assert len(response_json['descendants']) == post_comments[0].get_children_count()
        assert f"'id': {len(post_comments)}" in str(response_json)

    @pytest.mark.django_db
    def test_update_post_settings_valid_data(self, api_client, user, new_post):
        settings = {
            'is_ai_reply': True,
            'time_sleep': 60,
            'creativity': 1.0,
            'reply_or_dialogue': ReplyDialogue.DIALOGUE,
            'base_reply': 'Stop talking',
        }
        token = create_token(user)
        response = api_client.patch(f'/{new_post.id}/settings', json=settings,
                                    headers={'Authorization': f'Bearer {token}'})
        assert 200 == response.status_code
        response_json = response.json()
        new_post_settings = new_post.settings.get()
        assert response_json['is_ai_reply'] == new_post_settings.is_ai_reply
        assert response_json['time_sleep'] == new_post_settings.time_sleep
        assert response_json['creativity'] == new_post_settings.creativity
        assert response_json['reply_or_dialogue'] == new_post_settings.reply_or_dialogue
        assert response_json['base_reply'] == new_post_settings.base_reply

    @pytest.mark.django_db
    def test_update_post_settings_invalid_data(self, api_client, user, new_post):
        settings = {
            'is_ai_reply': True,
            'time_sleep': 60,
            'creativity': 1.5,
            'reply_or_dialogue': 5,
            'base_reply': '',
        }
        token = create_token(user)
        response = api_client.patch(f'/{new_post.id}/settings', json=settings,
                                    headers={'Authorization': f'Bearer {token}'})
        assert response.status_code == 422
        response_json = response.json()
        assert response_json['detail'][0]['msg'] == 'Input should be less than or equal to 1'

    @pytest.mark.django_db
    def test_comments_daily_breakdown_success(self, api_client, user, daily_breakdown_data):
        token = create_token(user)
        url = f'/daily-breakdown?date_from={daily_breakdown_data.date_from}&date_to={daily_breakdown_data.date_to}'
        response = api_client.get(url, headers={'Authorization': f'Bearer {token}'})
        assert response.status_code == 200
        response_json = response.json()
        assert daily_breakdown_data.date_from in response_json
        assert daily_breakdown_data.date_to in response_json
        date_from = datetime.strptime(daily_breakdown_data.date_from, '%Y-%m-%d').date()
        date_to = datetime.strptime(daily_breakdown_data.date_to, '%Y-%m-%d').date()
        posts = daily_breakdown_data.filter(depth=1).order_by('path')
        comments = daily_breakdown_data.exclude(depth=1).order_by('path')
        post_2_blocked_comments = comments.filter(
            path__startswith=posts[1].path,
            depth__gte=posts[1].depth,
            created_date__date=date_from,
            is_blocked=True)
        post_2_clean_comments = comments.filter(
            path__startswith=posts[1].path,
            depth__gte=posts[1].depth,
            created_date__date=date_from,
            is_blocked=False)
        assert response_json[daily_breakdown_data.date_from][f'post № {posts[1].id}'][
                   'blocked_comments'] == len(post_2_blocked_comments)
        assert response_json[daily_breakdown_data.date_from][f'post № {posts[1].id}'][
                   'clean_comments'] == len(post_2_clean_comments)
        assert response_json[daily_breakdown_data.date_from]['total_blocked_comments'] == len(comments.filter(
            created_date__date=date_from,
            is_blocked=True))
        assert response_json[daily_breakdown_data.date_from]['total_clean_comments'] == len(comments.filter(
            created_date__date=date_from,
            is_blocked=False))
        post_1_blocked_comments = comments.filter(
            path__startswith=posts[0].path,
            depth__gte=posts[0].depth,
            created_date__date=date_to,
            is_blocked=True)
        post_1_clean_comments = comments.filter(
            path__startswith=posts[0].path,
            depth__gte=posts[0].depth,
            created_date__date=date_to,
            is_blocked=False)
        assert response_json[daily_breakdown_data.date_to][f'post № {posts[0].id}'][
                   'blocked_comments'] == len(post_1_blocked_comments)
        assert response_json[daily_breakdown_data.date_to][f'post № {posts[0].id}'][
                   'clean_comments'] == len(post_1_clean_comments)
        assert response_json[daily_breakdown_data.date_to]['total_blocked_comments'] == len(comments.filter(
            created_date__date=date_to,
            is_blocked=True))
        assert response_json[daily_breakdown_data.date_to]['total_clean_comments'] == len(comments.filter(
            created_date__date=date_to,
            is_blocked=False))

    @pytest.mark.django_db
    def test_comments_daily_breakdown_wrong_period(self, api_client, user, ):
        token = create_token(user)
        date_to = datetime.now()
        date_from = date_to - timedelta(days=4)
        date_to = date_to.strftime('%Y-%m-%d')
        date_from = date_from.strftime('%Y-%m-%d')
        url = f'/daily-breakdown?date_from={date_from}&date_to={date_to}'
        response = api_client.get(url, headers={'Authorization': f'Bearer {token}'})
        assert response.status_code == 200
        response_json = response.json()
        assert date_from in response_json
        assert date_to in response_json
        assert 'post №' not in response_json[date_from]
        assert 'post №' not in response_json[date_to]
        assert response_json[date_from]['total_blocked_comments'] == 0
        assert response_json[date_from]['total_clean_comments'] == 0
        assert response_json[date_to]['total_blocked_comments'] == 0
        assert response_json[date_to]['total_clean_comments'] == 0
