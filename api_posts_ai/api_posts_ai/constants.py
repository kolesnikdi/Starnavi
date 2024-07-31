from django.db import models


class ReplyDialogue(models.IntegerChoices):
    REPLY = 1
    DIALOGUE = 2
