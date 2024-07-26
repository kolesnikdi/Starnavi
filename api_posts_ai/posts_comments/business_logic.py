from posts_comments.schemas import RetrievePostSchema


def cascade_display(post_comment):
    data = RetrievePostSchema.from_orm(post_comment).dict()
    descendants = post_comment.get_descendants()
    if descendants.exists():
        data['descendants'] = [cascade_display(descendant) for descendant in descendants]
    return data
