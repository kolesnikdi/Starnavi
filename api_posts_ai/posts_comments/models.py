from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.core.validators import MinValueValidator, MaxValueValidator
from django.dispatch import receiver
from treebeard.mp_tree import MP_Node
import time

from api_posts_ai.constants import ReplyDialogue
from api_posts_ai.gemini_api import ai


class Post(MP_Node):
    user = models.ForeignKey(User, related_name='posts', on_delete=models.DO_NOTHING)
    text = models.CharField(max_length=102400)  # max 100kb
    created_date = models.DateTimeField(auto_now=True)
    is_blocked = models.BooleanField(default=False)
    is_ai_comment = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)


class PostSettings(models.Model):
    post = models.ForeignKey(Post, related_name='settings', on_delete=models.CASCADE)
    is_ai_reply = models.BooleanField(default=False)
    # max time_sleep = 2 hours
    time_sleep = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(7200)], default=0)
    creativity = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)], default=0.5)
    reply_or_dialogue = models.SmallIntegerField(choices=ReplyDialogue.choices, default=ReplyDialogue.REPLY)
    base_reply = models.CharField(max_length=1024, default='I\'m not available right now. I will answer later')


@receiver(post_save, sender=Post)
def create_ai_reply(sender, instance: Post, created: bool, **kwargs):
    # It's better to send to Celery
    if created and not instance.is_root() and not instance.is_blocked and not instance.is_ai_comment:
        post = instance.get_root()
        post_settings = post.settings.get()
        if not post_settings.is_ai_reply:
            return
        if post_settings.reply_or_dialogue == ReplyDialogue.REPLY:
            parent = instance.get_parent()
            if not parent.is_root():
                return
            messages = [{'role': 'model', 'parts': [post.text]}, {'role': 'user', 'parts': [instance.text]}]
            time.sleep(post_settings.time_sleep)
            if not (reply := ai.reply(messages, post_settings.creativity)):
                reply = post_settings.base_reply
            instance.add_child(user_id=post.user.id, text=reply, is_ai_comment=True)
        if post_settings.reply_or_dialogue == ReplyDialogue.DIALOGUE:
            time.sleep(post_settings.time_sleep)
            tree_queryset = Post.get_tree(post)
            dialogue_queryset = tree_queryset.filter(user_id__in=[post.user.id, instance.user.id])
            roles = ['model', 'user']
            messages = []
            for number, comment in enumerate(dialogue_queryset):
                role = roles[number % 2]
                messages.append({'role': role, 'parts': [comment.text]})
            if not (reply := ai.reply(messages, post_settings.creativity)):
                reply = post_settings.base_reply
            instance.add_child(user_id=post.user.id, text=reply, is_ai_comment=True)
        else:
            return
    else:
        return
