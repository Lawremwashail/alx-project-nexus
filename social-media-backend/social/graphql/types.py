import graphene
from graphene_django import DjangoObjectType
from django.contrib.auth import get_user_model
from social.models import Post, Comment, Interaction, Follower, Notification

User = get_user_model()

class UserType(DjangoObjectType):
    class Meta:
        model = User
        # pick fields you want exposed; "__all__" is okay but be cautious
        fields = "__all__"


class PostType(DjangoObjectType):
    comments_count = graphene.Int()
    likes_count = graphene.Int()
    # expose resolved media url (prefers image.url if available)
    media_url = graphene.String()

    class Meta:
        model = Post
        fields = ("id", "author", "content", "image", "media_url", "created_at", "updated_at", "comments", "interactions")

    def resolve_comments_count(self, info):
        # self is a model instance when returned via DjangoObjectType
        return self.comments.count()

    def resolve_likes_count(self, info):
        return self.interactions.filter(type='like').count()

    def resolve_media_url(self, info):
        # if image is present return its URL; otherwise return media_url field
        try:
            if self.image and hasattr(self.image, "url"):
                return info.context.build_absolute_uri(self.image.url) if hasattr(info.context, "build_absolute_uri") else self.image.url
        except Exception:
            pass
        return self.media_url or None


class CommentType(DjangoObjectType):
    class Meta:
        model = Comment
        fields = ("id", "post", "user", "content", "type", "created_at")


class InteractionType(DjangoObjectType):
    class Meta:
        model = Interaction
        fields = ("id", "post", "user", "type", "content", "created_at")


class FollowerType(DjangoObjectType):
    class Meta:
        model = Follower
        fields = ("id", "follower", "following", "created_at")


class NotificationType(DjangoObjectType):
    class Meta:
        model = Notification
        fields = ("id", "recipient", "actor", "post", "message", "is_read", "created_at")

