import graphene
from graphene_django import DjangoObjectType
from social.models import Post, Comment, Like, Share


# GraphQL type representing the Post model.
# Exposes all Post model fields to the GraphQL API.
class PostType(DjangoObjectType):
    class Meta:
        model = Post
        fields = "__all__"


# GraphQL type representing the Comment model.
# Exposes all Comment model fields to the GraphQL API.
class CommentType(DjangoObjectType):
    class Meta:
        model = Comment
        fields = "__all__"


# GraphQL type representing the Like model.
# Exposes all Like model fields to the GraphQL API.
class LikeType(DjangoObjectType):
    class Meta:
        model = Like
        fields = "__all__"

# GraphQL type representing the Share model.
# Exposes all Share model fields to the GraphQL API.
class ShareType(DjangoObjectType):
    class Meta:
        model = Share
        fields = "__all__"
