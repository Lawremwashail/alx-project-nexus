from celery import shared_task
from django.contrib.auth import get_user_model
from social.models import Post, Comment, Interaction, Follower, Notification

User = get_user_model()

@shared_task
def process_comment(user_id, post_id, content):
    try:
        user = User.objects.get(id=user_id)
        post = Post.objects.get(id=post_id)
    except (User.DoesNotExist, Post.DoesNotExist):
        return None

    comment = Comment.objects.create(post=post, user=user, content=content)

    if post.author != user:
        Notification.objects.create(
            recipient=post.author,
            actor=user,
            post=post,
            message=f"{getattr(user, 'username', str(user))} commented on your post"
        )
    return comment.id

@shared_task
def process_interaction(user_id, post_id, interaction_type):
    try:
        user = User.objects.get(id=user_id)
        post = Post.objects.get(id=post_id)
    except (User.DoesNotExist, Post.DoesNotExist):
        return False

    Interaction.objects.get_or_create(user=user, post=post, type=interaction_type)

    if post.author != user:
        Notification.objects.create(
            recipient=post.author,
            actor=user,
            post=post,
            message=f"{getattr(user, 'username', str(user))} {interaction_type}d your post"
        )
    return True

@shared_task
def process_follow(user_id, target_id):
    try:
        user = User.objects.get(id=user_id)
        target = User.objects.get(id=target_id)
    except User.DoesNotExist:
        return False

    Follower.objects.get_or_create(follower=user, following=target)
    Notification.objects.create(
        recipient=target,
        actor=user,
        message=f"{getattr(user, 'username', str(user))} started following you"
    )
    return True

@shared_task
def process_unfollow(user_id, target_id):
    try:
        user = User.objects.get(id=user_id)
        target = User.objects.get(id=target_id)
    except User.DoesNotExist:
        return False

    Follower.objects.filter(follower=user, following=target).delete()
    return True

