from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.core.validators import MinValueValidator, MaxValueValidator
from django.dispatch import receiver
from treebeard.mp_tree import MP_Node
import time

from api_posts_ai.gemini_api import perform_ai_task_or_dialogue


class Post(MP_Node):
    user = models.ForeignKey(User, related_name='posts', on_delete=models.DO_NOTHING)
    text = models.CharField(max_length=102400)     # max 100kb
    created_date = models.DateTimeField(auto_now=True)
    is_blocked = models.BooleanField(default=False)
    # is_ai_comment = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class PostSettings(models.Model):
    post = models.ForeignKey(Post, related_name='settings', on_delete=models.CASCADE)
    is_ai_reply = models.BooleanField(default=False)
    time_sleep = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(7200)], default=0)
    creativity = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)], default=0.5)


@receiver(post_save, sender=Post)
def create_post_settings(sender, instance, created, **kwargs):
    if created and instance.is_root() and instance.is_blocked is False:
    # if created and instance.is_root() and not instance.is_blocked:
        PostSettings.objects.create(post=instance)
    if created and not instance.is_root() and instance.is_blocked is False:
        post = instance.get_root()
        if post.settings.is_ai_reply is True:
            time.sleep(post.settings.timesleep)
            # Якщо нема кеша
            messages = [{'role': 'model', 'parts': [post.text]}, {'role': 'user', 'parts': [instance.text]}]
            reply = perform_ai_task_or_dialogue(messages, post.settings.time_sleep)  # обробити Exception
            messages.append({'role': 'model', 'parts': [reply]})
            # Зберегти в кеш
            # Якщо кеш
            # дістати
            messages.append({'role': 'user', 'parts': [instance.text]})
            reply = perform_ai_task_or_dialogue(messages, post.settings.time_sleep)  # обробити Exception
            messages.append({'role': 'model', 'parts': [reply]})
            # Зберегти в кеш
