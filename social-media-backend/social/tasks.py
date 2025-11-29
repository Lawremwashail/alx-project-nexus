from celery import shared_task
from django.contrib.auth import get_user_model
from social.models import Post, Comment, Interaction, Follower, Notification

User = get_user_model()


# ---------------------------------------------------------
# ASYNC: CREATE COMMENT
# ---------------------------------------------------------
@shared_task
def process_comment(user_id, post_id, content):
    try:
        user = User.objects.get(id=user_id)
        post = Post.objects.get(id=post_id)
    except (User.DoesNotExist, Post.DoesNotExist):
        return None

    comment = Comment.objects.create(
        post=post,
        user=user,
        content=content
    )

    # Send notification
    if post.author != user:
        Notification.objects.create(
            recipient=post.author,
            actor=user,
            post=post,
            message=f"{user.username} commented on your post"
        )

    return comment.id


# ---------------------------------------------------------
# ASYNC: LIKE / SHARE / REACTION 
# (ALL in ONE handler)
# ---------------------------------------------------------
@shared_task
def process_interaction(user_id, post_id, interaction_type, content=None):
    """
    interaction_type = 'like', 'share', 'reaction'
    content = optional: reaction name, share text
    """
    try:
        user = User.objects.get(id=user_id)
        post = Post.objects.get(id=post_id)
    except (User.DoesNotExist, Post.DoesNotExist):
        return False

    # Create or update interaction (unique per user/post/type)
    interaction, created = Interaction.objects.get_or_create(
        user=user,
        post=post,
        type=interaction_type,
        defaults={'content': content}
    )

    if not created:
        # If interaction exists, update content (for reactions)
        if content:
            interaction.content = content
            interaction.save(update_fields=["content"])

    # Notifications
    if post.author != user:
        msg = ""

        if interaction_type == "like":
            msg = f"{user.username} liked your post"
        elif interaction_type == "share":
            msg = f"{user.username} shared your post"
        elif interaction_type == "reaction":
            reaction_name = content or "reacted"
            msg = f"{user.username} reacted ({reaction_name}) to your post"

        Notification.objects.create(
            recipient=post.author,
            actor=user,
            post=post,
            message=msg
        )

    return True


# ---------------------------------------------------------
# ASYNC: FOLLOW USER
# ---------------------------------------------------------
@shared_task
def process_follow(user_id, target_id):
    try:
        user = User.objects.get(id=user_id)
        target = User.objects.get(id=target_id)
    except User.DoesNotExist:
        return False

    follow, created = Follower.objects.get_or_create(
        follower=user,
        following=target
    )

    if created:
        Notification.objects.create(
            recipient=target,
            actor=user,
            message=f"{user.username} started following you"
        )

    return True


# ---------------------------------------------------------
# ASYNC: UNFOLLOW USER
# ---------------------------------------------------------
@shared_task
def process_unfollow(user_id, target_id):
    try:
        user = User.objects.get(id=user_id)
        target = User.objects.get(id=target_id)
    except User.DoesNotExist:
        return False

    Follower.objects.filter(
        follower=user,
        following=target
    ).delete()

    return True

