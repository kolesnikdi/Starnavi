from django.db.models import QuerySet

from collections import defaultdict
from datetime import timedelta, date, datetime, time
import pytz

from posts_comments.models import Post
from posts_comments.schemas import PostSortSchema


def cascade_display(queryset: QuerySet):
    tree_dict = defaultdict(list)
    post = queryset.first()
    comments_queryset = queryset.exclude(id=post.id)
    for comment in comments_queryset:
        tree_dict[comment.path[:-4]].append(comment)

    def build_response(post_comment: int):
        post_comments_data = PostSortSchema.from_orm(post_comment).dict()
        comments = tree_dict.get(post_comment.path, [])
        if comments:
            post_comments_data['descendants'] = [build_response(comment) for comment in comments]
        return post_comments_data

    return build_response(post)


def make_daily_breakdown(date_from: date, date_to: date):
    # tzinfo = pytz.UTC
    # date_from = tzinfo.localize(datetime.combine(date_from, time.min))
    # date_to = tzinfo.localize(datetime.combine(date_to, time.max))
    daily_breakdown = {}
    all_posts_comments = Post.objects.filter(created_date__date__range=(date_from, date_to))
    posts = all_posts_comments.filter(depth=1).order_by('path')
    comments = all_posts_comments.exclude(depth=1).order_by('path')
    for n in range((date_to - date_from).days + 1):
        date = date_from + timedelta(days=n)
        date_str = date.strftime('%Y-%m-%d')
        daily_breakdown.setdefault(date_str, {'total_blocked_comments': 0, 'total_clean_comments': 0})

        for post in posts:
            blocked_comments = comments.filter(
                path__startswith=post.path,
                depth__gte=post.depth,
                created_date__date=date,
                is_blocked=True)
            clean_comments = comments.filter(
                path__startswith=post.path,
                depth__gte=post.depth,
                created_date__date=date,
                is_blocked=False)
            count_blocked_comments = len(blocked_comments)
            count_clean_comments = len(clean_comments)
            if count_blocked_comments and count_clean_comments:
                daily_breakdown[date_str].setdefault(
                    f'post № {post.id}',
                    {'blocked_comments': count_blocked_comments, 'clean_comments': count_clean_comments})
            daily_breakdown[date_str]['total_blocked_comments'] += count_blocked_comments
            daily_breakdown[date_str]['total_clean_comments'] += count_clean_comments

    return daily_breakdown
