import graphene
from graphene_django import DjangoObjectType
from django.contrib.auth import get_user_model
from social.models import (
    Post,
    Comment,
    Interaction,
    Follower,
    Notification
)

User = get_user_model()


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("id", "username", "email")


class PostType(DjangoObjectType):
    class Meta:
        model = Post
        fields = "__all__"

    author = graphene.Field(UserType)

    def resolve_author(self, info):
        return self.author
    


class CommentType(DjangoObjectType):
    class Meta:
        model = Comment
        fields = "__all__"


class InteractionType(DjangoObjectType):
    class Meta:
        model = Interaction
        fields = "__all__"


class FollowerType(DjangoObjectType):
    class Meta:
        model = Follower
        fields = "__all__"


class NotificationType(DjangoObjectType):
    class Meta:
        model = Notification
        fields = "__all__"

