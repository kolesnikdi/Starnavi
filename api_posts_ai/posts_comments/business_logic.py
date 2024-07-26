from posts_comments.schemas import RetrievePostSchema


# def validate_text(text):
#     open_tags = re.findall(r'<([^/][^>]*)>', text)
#     cleaned_open_tags = [tag.split()[0] if ' ' in tag else tag for tag in open_tags]
#     closed_tags = re.findall(r'</([^>]*)>', text)
#     cleaned_closed_tags = [tag.split()[0] if ' ' in tag else tag for tag in closed_tags]
#     if cleaned_open_tags != cleaned_closed_tags:
#         return {'error': 'Verify your text. You have open Tags'}
#
#     for tag in cleaned_open_tags:
#         if tag not in ['a', 'code', 'i', 'strong']:
#             return {'error': 'Use only allowed Tags: <a href=”” title=””> </a> <code> </code> <i> </i>'
#                              ' <strong> </strong>'}


def cascade_display(post_comment):
    data = RetrievePostSchema.from_orm(post_comment).dict()
    descendants = post_comment.get_descendants()
    if descendants.exists():
        data['descendants'] = [cascade_display(descendant) for descendant in descendants]
    return data
