import graphene
from graphene import relay
from django.db.models import Prefetch
from social.models import Post, Comment, Interaction, Follower, Notification
from .types import PostType, CommentType, InteractionType, FollowerType, NotificationType, UserType
from django.contrib.auth import get_user_model

User = get_user_model()

class SocialQuery(graphene.ObjectType):
    # Posts
    all_posts = graphene.List(PostType, first=graphene.Int(), offset=graphene.Int())
    post = graphene.Field(PostType, id=graphene.ID(required=True))

    # Comments
    comments_for_post = graphene.List(CommentType, post_id=graphene.ID(required=True))

    # Interactions
    interactions_for_post = graphene.List(InteractionType, post_id=graphene.ID(required=True))

    # Followers / followees
    followers = graphene.List(FollowerType, user_id=graphene.ID(required=True))
    following = graphene.List(FollowerType, user_id=graphene.ID(required=True))

    # Notifications
    notifications_for_user = graphene.List(NotificationType, user_id=graphene.ID(required=True), unread_only=graphene.Boolean())

    # Simple user query
    user = graphene.Field(UserType, id=graphene.ID(required=True))

    # Resolvers
    def resolve_all_posts(self, info, first=None, offset=None):
        qs = Post.objects.select_related("author").prefetch_related(
            Prefetch("comments", queryset=Comment.objects.select_related("user").order_by("-created_at")),
            Prefetch("interactions", queryset=Interaction.objects.select_related("user"))
        ).order_by("-created_at")
        if offset:
            qs = qs[offset:]
        if first:
            qs = qs[:first]
        return qs

    def resolve_post(self, info, id):
        return Post.objects.select_related("author").prefetch_related("comments", "interactions").get(id=id)

    def resolve_comments_for_post(self, info, post_id):
        return Comment.objects.filter(post_id=post_id).select_related("user").order_by("created_at")

    def resolve_interactions_for_post(self, info, post_id):
        return Interaction.objects.filter(post_id=post_id).select_related("user").order_by("-created_at")

    def resolve_followers(self, info, user_id):
        return Follower.objects.filter(following_id=user_id).select_related("follower", "following")

    def resolve_following(self, info, user_id):
        return Follower.objects.filter(follower_id=user_id).select_related("follower", "following")

    def resolve_notifications_for_user(self, info, user_id, unread_only=False):
        qs = Notification.objects.filter(recipient_id=user_id).select_related("actor", "post").order_by("-created_at")
        if unread_only:
            qs = qs.filter(is_read=False)
        return qs

    def resolve_user(self, info, id):
        return User.objects.get(id=id)

