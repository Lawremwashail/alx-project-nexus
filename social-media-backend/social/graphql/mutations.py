import graphene
from graphql import GraphQLError
from django.contrib.auth import get_user_model

from social.models import Post, Comment, Interaction, Follower, Notification
from .types import (
    PostType, CommentType, InteractionType,
    FollowerType, NotificationType
)
from .auth import RegisterUser


# Celery tasks
from social.tasks import (
    process_comment,
    process_interaction,
    process_follow,
    process_unfollow
)

User = get_user_model()


# --------------------------------------------------
# AUTH DECORATOR
# --------------------------------------------------
def login_required(func):
    def wrapper(root, info, *args, **kwargs):
        user = getattr(info.context, "user", None)
        if not user or user.is_anonymous:
            raise GraphQLError("Authentication required")
        return func(root, info, *args, **kwargs)
    return wrapper


# --------------------------------------------------
# CREATE POST
# --------------------------------------------------
class CreatePost(graphene.Mutation):
    class Arguments:
        content = graphene.String(required=True)
        media_url = graphene.String(required=False)

    post = graphene.Field(PostType)

    @login_required
    def mutate(self, info, content, media_url=None):
        user = info.context.user
        post = Post.objects.create(
            author=user,
            content=content,
            media_url=media_url
        )
        return CreatePost(post=post)


# --------------------------------------------------
# ADD COMMENT
# (ASYNC via Celery)
# --------------------------------------------------
class AddComment(graphene.Mutation):
    class Arguments:
        post_id = graphene.ID(required=True)
        content = graphene.String(required=True)

    ok = graphene.Boolean()

    @login_required
    def mutate(self, info, post_id, content):
        user = info.context.user
        process_comment.delay(user.id, int(post_id), content)
        return AddComment(ok=True)


# --------------------------------------------------
# LIKE / REACTION / SHARE  
# (ALL VIA Interaction MODEL + Celery)
# --------------------------------------------------
class AddInteraction(graphene.Mutation):
    class Arguments:
        post_id = graphene.ID(required=True)
        type = graphene.String(required=True)   # "like", "share", "reaction"
        content = graphene.String(required=False)  # e.g., reaction name

    ok = graphene.Boolean()

    @login_required
    def mutate(self, info, post_id, type, content=None):
        user = info.context.user

        valid = ["like", "share", "reaction"]
        if type not in valid:
            raise GraphQLError("Invalid interaction type")

        process_interaction.delay(
            user.id,
            int(post_id),
            type,
            content
        )

        return AddInteraction(ok=True)


# --------------------------------------------------
# FOLLOW USER
# --------------------------------------------------
class FollowUser(graphene.Mutation):
    class Arguments:
        user_id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @login_required
    def mutate(self, info, user_id):
        user = info.context.user
        process_follow.delay(user.id, int(user_id))
        return FollowUser(ok=True)


# --------------------------------------------------
# UNFOLLOW USER
# --------------------------------------------------
class UnfollowUser(graphene.Mutation):
    class Arguments:
        user_id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @login_required
    def mutate(self, info, user_id):
        user = info.context.user
        process_unfollow.delay(user.id, int(user_id))
        return UnfollowUser(ok=True)


# --------------------------------------------------
# MARK NOTIFICATION READ
# --------------------------------------------------
class MarkNotificationRead(graphene.Mutation):
    class Arguments:
        notification_id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @login_required
    def mutate(self, info, notification_id):
        user = info.context.user

        try:
            notif = Notification.objects.get(
                id=notification_id,
                recipient=user
            )
        except Notification.DoesNotExist:
            raise GraphQLError("Notification not found")

        notif.is_read = True
        notif.save(update_fields=["is_read"])

        return MarkNotificationRead(ok=True)


# --------------------------------------------------
# ROOT MUTATION
# --------------------------------------------------
class Mutation(graphene.ObjectType):
    create_post = CreatePost.Field()
    add_comment = AddComment.Field()
    add_interaction = AddInteraction.Field()
    follow_user = FollowUser.Field()
    unfollow_user = UnfollowUser.Field()
    mark_notification_read = MarkNotificationRead.Field()
    register_user = RegisterUser.Field()
