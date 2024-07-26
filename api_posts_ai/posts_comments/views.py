from django.shortcuts import get_object_or_404

from ninja import Router

from api_posts_ai.authentication import AuthBearer
from posts_comments.business_logic import cascade_display
from posts_comments.models import Post
from posts_comments.schemas import PostSchema, RetrievePostSchema, RetrievePostCommentsSchema
from users.schemas import ErrorSchema

post_router = Router()


@post_router.post('/create', auth=AuthBearer(), response={201: RetrievePostSchema, 400: ErrorSchema})
def create_post(request, text: PostSchema):
    user = request.auth
    post = Post.add_root(user_id=user.id, text=text['text'])
    return 201, post


@post_router.post('/{post_id}/create', auth=AuthBearer(), response={201: RetrievePostSchema, 404: ErrorSchema})
def create_comment(request, text: PostSchema, post_id: int):
    user = request.auth
    post = get_object_or_404(Post, id=post_id)
    comment = post.add_child(user_id=user.id, text=text['text'])
    return 201, comment

@post_router.put('/{post_id}/update', auth=AuthBearer(), response={200: RetrievePostSchema, 404: ErrorSchema})
def update_post_comment(request, text: PostSchema, post_id: int):
    user = request.auth
    post_comment = get_object_or_404(Post, id=post_id)
    if user.id == post_comment.user_id:
        post_comment.text = text['text']
        post_comment.save()
        return 200, post_comment
    return 404, {'error': 'This action is allowed only to the owner'}


@post_router.delete('/{post_id}/delete', auth=AuthBearer(), response={204: dict, 400: ErrorSchema})
def delete_post_comment(request, post_id: int):
    user = request.auth
    post_comment = get_object_or_404(Post, id=post_id)
    if user.id == post_comment.user_id:
        if post_comment.is_leaf():
            post_comment.delete()
            return 204, {"detail": "It was deleted successfully"}
        return 400, {'error': 'You cannot delete a post with comments to it'}
    return 400, {'error': 'This action is allowed only to the owner'}


# @post_router.get('/{post_id}', auth=AuthBearer(), response={200: RetrievePostCommentsSchema, 400: ErrorSchema})
@post_router.get('/{post_id}', response={200: RetrievePostCommentsSchema, 404: ErrorSchema})
def get_post_comment(request, post_id: int):
    post_comment = get_object_or_404(Post, id=post_id)
    return 200, cascade_display(post_comment)
