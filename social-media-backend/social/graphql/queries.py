import graphene
from social.models import Post, Comment
from .types import PostType, CommentType


# Query class that exposes read operations for posts.
# Provides access to all posts and to a specific post using its ID.
class Query(graphene.ObjectType):
    # Returns a list of all posts, represented using the PostType GraphQL type.
    all_posts = graphene.List(PostType)

    # Returns a single post corresponding to the provided ID.
    post_by_id = graphene.Field(PostType, id=graphene.Int(required=True))
    
    # Resolver for retrieving all posts, ordered by creation timestamp (newest first).
    def resolve_all_posts(root, info):
        return Post.objects.all().order_by("-created_at")

    # Resolver for retrieving a specific post using its unique ID.
    def resolve_post_by_id(root, info, id):
        return Post.objects.get(id=id)
