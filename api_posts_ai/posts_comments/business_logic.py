from api_posts_ai.gemini_api import perform_ai_task_or_dialogue
from posts_comments.schemas import RetrievePostSchema


def cascade_display(post_comment):
    data = RetrievePostSchema.from_orm(post_comment).dict()
    descendants = post_comment.get_descendants().filter(is_blocked=False)
    if descendants.exists():
        data['descendants'] = [cascade_display(descendant) for descendant in descendants]
    return data


"""Its better to send to Celery"""
def is_swearing(text):
    task = f"Answer to me only in English. If the text '{text}'does not contain any swear words, your answer must be '0'"
    try:
        safety = int(perform_ai_task_or_dialogue(task, 1.0))
        return safety
    except ValueError as e:
        if 'candidate.safety_ratings' or 'int()' in e.args[0]:
            return True
        return False
    except Exception:
        return False
