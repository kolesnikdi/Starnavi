from django.contrib import admin
from posts_comments.models import Post, PostSettings

admin.site.register(Post)
admin.site.register(PostSettings)
