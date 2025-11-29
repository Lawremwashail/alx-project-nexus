import graphene
from graphql import GraphQLError
from django.contrib.auth import get_user_model

from social.models import Post, Comment, Interaction, Follower, Notification
from .types import (
    UserType,
    PostType,
    CommentType,
    InteractionType,
    FollowerType,
    NotificationType
)

User = get_user_model()

# -------------------------------
# Authentication decorator
# -------------------------------
def login_required(func):
    def wrapper(root, info, *args, **kwargs):
        user = getattr(info.context, "user", None)
        if not user or user.is_anonymous:
            raise GraphQLError("Authentication required")
        return func(root, info, *args, **kwargs)
    return wrapper


# -------------------------------
# Query Definitions
# -------------------------------
class Query(graphene.ObjectType):
    # User
    me = graphene.Field(UserType)
    user_profile = graphene.Field(UserType, user_id=graphene.ID(required=True))
    
    # Posts
    posts = graphene.List(
        PostType,
        limit=graphene.Int(required=False),
        offset=graphene.Int(required=False),
        sort_by=graphene.String(required=False)
    )
    
    post = graphene.Field(PostType, post_id=graphene.ID(required=True))
    
    # Comments
    comments_by_post = graphene.List(CommentType, post_id=graphene.ID(required=True))
    
    # Interactions
    interactions_by_post = graphene.List(InteractionType, post_id=graphene.ID(required=True))
    
    # Followers
    followers = graphene.List(FollowerType, user_id=graphene.ID(required=True))
    following = graphene.List(FollowerType, user_id=graphene.ID(required=True))
    
    # Notifications
    my_notifications = graphene.List(NotificationType)

    # -------------------------------
    # Resolvers
    # -------------------------------

    # Authenticated user
    @login_required
    def resolve_me(self, info):
        return info.context.user
    
    

    # Get profile by ID
    def resolve_user_profile(self, info, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise GraphQLError("User not found")

    # Posts list with pagination & sorting
    def resolve_posts(self, info, limit=None, offset=None, sort_by=None):
        user = info.context.user
        qs = Post.objects.filter(author=user)

        if sort_by == "recent":
            qs = qs.order_by("-created_at")
        elif sort_by == "popular":
            qs = qs.order_by("-like_count")
        else:
            qs = qs.order_by("-created_at")

        if offset is not None:
            qs = qs[offset:]
        if limit is not None:
            qs = qs[:limit]

        return qs

    # Single post
    def resolve_post(self, info, post_id):
        try:
            return Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            raise GraphQLError("Post not found")

    # Comments for a post
    def resolve_comments_by_post(self, info, post_id):
        return Comment.objects.filter(post_id=post_id).order_by("-created_at")

    # Interactions (likes, shares)
    def resolve_interactions_by_post(self, info, post_id):
        return Interaction.objects.filter(post_id=post_id).order_by("-created_at")

    # Followers list
    def resolve_followers(self, info, user_id):
        return Follower.objects.filter(following_id=user_id)

    # Following list
    def resolve_following(self, info, user_id):
        return Follower.objects.filter(follower_id=user_id)

    # Notifications for logged-in user
    @login_required
    def resolve_my_notifications(self, info):
        user = info.context.user
        return Notification.objects.filter(recipient=user).order_by("-created_at")

