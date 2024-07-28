from django.shortcuts import get_object_or_404

from ninja import Router

from api_posts_ai.authentication import AuthBearer
from posts_comments.business_logic import cascade_display, is_swearing
from posts_comments.models import Post
from posts_comments.schemas import PostSchema, RetrievePostSchema, RetrievePostCommentsSchema, PostSettingsSchema
from users.schemas import ErrorSchema

post_router = Router()


@post_router.post('/', auth=AuthBearer(), response={201: RetrievePostSchema, 400: ErrorSchema})
def create_post(request, data: PostSchema):
    user = request.auth
    if not is_swearing(data.text):
        post = Post.add_root(user_id=user.id, text=data.text)
        return 201, post
    Post.add_root(user_id=user.id, text=data.text, is_blocked=True)
    return 400, {'error': 'The text contains swear words.'}


@post_router.post('/{post_id}', auth=AuthBearer(), response={201: RetrievePostSchema, 400: ErrorSchema})
def create_comment(request, data: PostSchema, post_id: int):
    user = request.auth
    post = get_object_or_404(Post, id=post_id, is_blocked=False)
    if not is_swearing(data.text):
        comment = post.add_child(user_id=user.id, text=data.text)
        return 201, comment
    post.add_child(user_id=user.id, text=data.text, is_blocked=True)
    return 400, {'error': 'The text contains swear words.'}

@post_router.patch('/{post_id}', auth=AuthBearer(), response={200: RetrievePostSchema, 405: ErrorSchema})
def update_post_comment(request, data: PostSchema, post_id: int):
    user = request.auth
    post_comment = get_object_or_404(Post, id=post_id, is_blocked=False)
    if user.id == post_comment.user_id:
        post_comment.text = data.text
        post_comment.save()
        return 200, post_comment
    return 405, {'error': 'This action is allowed only to the owner'}


@post_router.delete('/{post_id}', auth=AuthBearer(), response={204: dict, 405: ErrorSchema})
def delete_post_comment(request, post_id: int):
    user = request.auth
    post_comment = get_object_or_404(Post, id=post_id, is_blocked=False)
    if user.id == post_comment.user_id:
        if post_comment.is_leaf():
            post_comment.delete()
            return 204, {'detail': 'It was deleted successfully'}
        return 405, {'error': 'You cannot delete a post with comments to it'}
    return 405, {'error': 'This action is allowed only to the owner'}


@post_router.get('/{post_id}', auth=AuthBearer(), response={200: RetrievePostCommentsSchema, 400: ErrorSchema})
def get_post_comment(request, post_id: int):
    post_comment = get_object_or_404(Post, id=post_id, is_blocked=False)
    return 200, cascade_display(post_comment)


@post_router.patch('/{post_id}/settings', auth=AuthBearer(), response={200: PostSettingsSchema,
                                                                       400: ErrorSchema,
                                                                       405: ErrorSchema})
def update_post_settings(request, post_id: int, data: PostSettingsSchema):
    user = request.auth
    post = get_object_or_404(Post, id=post_id, is_blocked=False)
    if user.id == post.user_id:
        if data.is_ai_reply is True:
            post.settings.is_ai_reply = data.is_ai_reply
            post.settings.time_sleep = data.timesleep
            post.settings.creativity = data.creativity
            post.settings.save()
            return 200, post
        return 400, {'error': 'First you must turn on AI reply'}
    return 405, {'error': 'This action is allowed only to the owner'}
