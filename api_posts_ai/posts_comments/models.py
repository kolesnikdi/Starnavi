from django.contrib.auth.models import User
from django.db import models
from treebeard.mp_tree import MP_Node


class Post(MP_Node):
    user_id = models.ForeignKey(User, related_name='posts', on_delete=models.DO_NOTHING)
    text = models.CharField(max_length=102400)     # max 100kb
    created_date = models.DateTimeField(auto_now=True)
    is_blocked = models.BooleanField(default=False)
    is_ai_comment = models.BooleanField(default=False)

    def __str__(self):
        return self.text
