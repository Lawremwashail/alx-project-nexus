import graphene
from graphql import GraphQLError
from django.contrib.auth import get_user_model
from social.models import Post, Comment, Interaction, Follower, Notification
from .types import PostType, CommentType, InteractionType, FollowerType, NotificationType

User = get_user_model()

def login_required(func):
    def wrapper(root, info, *args, **kwargs):
        user = getattr(info.context, "user", None)
        if not user or user.is_anonymous:
            raise GraphQLError("Authentication required")
        return func(root, info, *args, **kwargs)
    return wrapper


class CreatePost(graphene.Mutation):
    class Arguments:
        content = graphene.String(required=True)
        media_url = graphene.String(required=False)
        # If you want to support file upload via GraphQL, you'd need django-graphql-jwt & multipart support
        # image_upload = graphene.String(required=False)  # placeholder

    post = graphene.Field(PostType)

    @login_required
    def mutate(self, info, content, media_url=None):
        user = info.context.user
        post = Post.objects.create(author=user, content=content, media_url=media_url)
        return CreatePost(post=post)


class AddComment(graphene.Mutation):
    class Arguments:
        post_id = graphene.ID(required=True)
        content = graphene.String(required=True)

    comment = graphene.Field(CommentType)

    @login_required
    def mutate(self, info, post_id, content):
        user = info.context.user
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            raise GraphQLError("Post not found")

        comment = Comment.objects.create(post=post, user=user, content=content)
        # Optionally create Notification for post author
        if post.author != user:
            Notification.objects.create(
                recipient=post.author,
                actor=user,
                post=post,
                message=f"{getattr(user, 'username', str(user))} commented on your post"
            )
        return AddComment(comment=comment)


class LikePost(graphene.Mutation):
    class Arguments:
        post_id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @login_required
    def mutate(self, info, post_id):
        user = info.context.user
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            raise GraphQLError("Post not found")

        Interaction.objects.get_or_create(user=user, post=post, type="like")
        if post.author != user:
            Notification.objects.create(
                recipient=post.author,
                actor=user,
                post=post,
                message=f"{getattr(user, 'username', str(user))} liked your post"
            )
        return LikePost(ok=True)


class SharePost(graphene.Mutation):
    class Arguments:
        post_id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @login_required
    def mutate(self, info, post_id):
        user = info.context.user
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            raise GraphQLError("Post not found")

        Interaction.objects.get_or_create(user=user, post=post, type="share")
        if post.author != user:
            Notification.objects.create(
                recipient=post.author,
                actor=user,
                post=post,
                message=f"{getattr(user, 'username', str(user))} shared your post"
            )
        return SharePost(ok=True)


class FollowUser(graphene.Mutation):
    class Arguments:
        user_id = graphene.ID(required=True)  # id to follow

    ok = graphene.Boolean()

    @login_required
    def mutate(self, info, user_id):
        user = info.context.user
        try:
            target = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise GraphQLError("User not found")

        if user == target:
            raise GraphQLError("Cannot follow yourself")
        Follower.objects.get_or_create(follower=user, following=target)
        Notification.objects.create(
            recipient=target,
            actor=user,
            message=f"{getattr(user, 'username', str(user))} started following you"
        )
        return FollowUser(ok=True)


class UnfollowUser(graphene.Mutation):
    class Arguments:
        user_id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @login_required
    def mutate(self, info, user_id):
        user = info.context.user
        try:
            target = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise GraphQLError("User not found")

        Follower.objects.filter(follower=user, following=target).delete()
        return UnfollowUser(ok=True)


class MarkNotificationRead(graphene.Mutation):
    class Arguments:
        notification_id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @login_required
    def mutate(self, info, notification_id):
        user = info.context.user
        try:
            notif = Notification.objects.get(id=notification_id, recipient=user)
        except Notification.DoesNotExist:
            raise GraphQLError("Notification not found")
        notif.is_read = True
        notif.save(update_fields=["is_read"])
        return MarkNotificationRead(ok=True)


class SocialMutation(graphene.ObjectType):
    create_post = CreatePost.Field()
    add_comment = AddComment.Field()
    like_post = LikePost.Field()
    share_post = SharePost.Field()
    follow_user = FollowUser.Field()
    unfollow_user = UnfollowUser.Field()
    mark_notification_read = MarkNotificationRead.Field()
