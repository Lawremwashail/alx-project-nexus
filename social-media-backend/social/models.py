from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# Post Model
class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    # keep both an uploaded image and an optional external media url
    image = models.ImageField(upload_to='post_images/', null=True, blank=True)
    media_url = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # guard in case of custom user model without username
        username = getattr(self.author, "username", str(self.author))
        return f"Post by {username} ({self.id})"


# Comment Model
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    type = models.CharField(max_length=50, default="text")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        username = getattr(self.user, "username", str(self.user))
        return f"Comment by {username} on Post {self.post_id}"


# Interaction Model
class Interaction(models.Model):
    INTERACTION_TYPES = (
        ('like', 'Like'),
        ('share', 'Share'),
        ('reaction', 'Reaction'),
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='interactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interactions')
    type = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    content = models.TextField(null=True, blank=True)  # e.g., reaction name or share text
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user', 'type')

    def __str__(self):
        username = getattr(self.user, "username", str(self.user))
        return f"{username} {self.type}d Post {self.post_id}"


# Follower Model
class Follower(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')   # users this user follows
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')  # users that follow this user
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')

    def __str__(self):
        f1 = getattr(self.follower, "username", str(self.follower))
        f2 = getattr(self.following, "username", str(self.following))
        return f"{f1} follows {f2}"


# Notification Model
class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='actions')
    post = models.ForeignKey(Post, null=True, blank=True, on_delete=models.SET_NULL)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        recipient_name = getattr(self.recipient, "username", str(self.recipient))
        return f"Notification to {recipient_name} - {self.message[:40]}"

