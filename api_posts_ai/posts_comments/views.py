from django.shortcuts import get_object_or_404

from ninja import Router

from api_posts_ai.authentication import AuthBearer
from api_posts_ai.gemini_api import ai
from posts_comments.business_logic import cascade_display, make_daily_breakdown
from posts_comments.models import Post, PostSettings
from posts_comments.schemas import CreatePostSchema, PostSchema, RetrievePostCommentsSchema, PostSettingsSchema, \
    DailyBreakdownResponseSchema
from users.schemas import ErrorSchema, DetailSchema
from datetime import date

post_router = Router()


@post_router.post('/', auth=AuthBearer(), response={201: PostSchema})
def create_post(request, data: CreatePostSchema):
    user = request.auth
    post_data = data.dict()
    post_data['user_id'] = user.id
    if ai.is_swearing(post_data["text"]):
        post_data["is_blocked"] = True
    post = Post.add_root(**post_data)
    PostSettings.objects.create(post=post)
    return 201, post


@post_router.get('/daily-breakdown', auth=AuthBearer(), response={200: DailyBreakdownResponseSchema})
def comments_daily_breakdown(request, date_from: date, date_to: date):
    # no conditions for who can view
    return 200, make_daily_breakdown(date_from, date_to)


@post_router.post('/{post_id}', auth=AuthBearer(), response={201: PostSchema})
def create_comment(request, data: CreatePostSchema, post_id: int):
    user = request.auth
    post = get_object_or_404(Post, id=post_id, is_blocked=False)
    post_data = data.dict()
    post_data['user_id'] = user.id
    if ai.is_swearing(post_data["text"]):
        post_data["is_blocked"] = True
    comment = post.add_child(**post_data)
    # optional runs Signal create_ai_reply()
    return 201, comment


@post_router.patch('/{post_id}', auth=AuthBearer(), response={200: PostSchema})
def update_post_comment(request, data: CreatePostSchema, post_id: int):
    user = request.auth
    post_comment = get_object_or_404(Post, id=post_id, is_blocked=False, user_id=user.id)
    if ai.is_swearing(data.text):
        post_comment.is_blocked = True
    post_comment.text = data.text
    post_comment.save()
    return 200, post_comment


@post_router.delete('/{post_id}', auth=AuthBearer(), response={204: DetailSchema, 403: ErrorSchema})
def delete_post_comment(request, post_id: int):
    user = request.auth
    post_comment = get_object_or_404(Post, id=post_id, is_blocked=False, user_id=user.id)
    if post_comment.is_leaf():
        post_comment.delete()
        return 204, {'detail': 'It was deleted successfully'}
    return 403, {'error': 'You cannot delete a post with comments to it'}


@post_router.get('/{post_id}', auth=AuthBearer(), response={200: RetrievePostCommentsSchema})
def get_post_comments(request, post_id: int):
    post_comment = get_object_or_404(Post, id=post_id, is_blocked=False)
    tree_queryset = Post.get_tree(post_comment)
    return 200, cascade_display(tree_queryset)


@post_router.patch('/{post_id}/settings', auth=AuthBearer(), response={200: PostSettingsSchema})
def update_post_settings(request, post_id: int, data: PostSettingsSchema):
    user = request.auth
    post_settings = get_object_or_404(PostSettings, post_id=post_id, post__user_id=user.id)
    post_settings.is_ai_reply = data.is_ai_reply
    post_settings.time_sleep = data.time_sleep
    post_settings.creativity = data.creativity
    post_settings.reply_or_dialogue = data.reply_or_dialogue
    post_settings.base_reply = data.base_reply
    post_settings.save()
    return 200, post_settings
