from django.contrib import admin
from .models import Post, Comment, Interaction, Follower, Notification

admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Interaction)
admin.site.register(Follower)
admin.site.register(Notification)

