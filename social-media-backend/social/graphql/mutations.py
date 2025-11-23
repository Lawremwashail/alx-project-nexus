import graphene
from social.models import Post, Comment, Like
from .types import PostType, CommentType


# Mutation for creating a new post.
# Accepts content as input and returns the newly created Post object.

class CreatePost(graphene.Mutation):
    class Arguments:
        content = graphene.String(required=True)   # Text content for the post.

    post = graphene.Field(PostType)  # GraphQL field returned after creation.


    def mutate(self, info, content):
        # Accessing the currently authenticated user from the request context.
        user = info.context.user
        if user.is_anonymous:
            # Restricts post creation to authenticated users.
            raise Exception("Authentication required")
        # Creating a new Post record associated with the authenticated user.
        post = Post.objects.create(author=user, content=content)
        return CreatePost(post=post)

# Mutation for adding a comment to an existing post.
# Requires the target post ID and the comment content.
class AddComment(graphene.Mutation):
    class Arguments:
        post_id = graphene.Int(required=True)  # ID of the post to comment on.
        content = graphene.String(required=True) # Comment text.

    comment = graphene.Field(CommentType)  # Returns the created Comment object.

    def mutate(self, info, post_id, content):
        # Obtains the current user and the post receiving the comment.
        user = info.context.user
        post = Post.objects.get(id=post_id)

        # Creating a new comment linked to the post and user.
        comment = Comment.objects.create(post=post, user=user, content=content)
        return AddComment(comment=comment)

# Mutation for liking a post.
# Produces a boolean indicating if the operation succeeded.
class LikePost(graphene.Mutation):
    class Arguments:
        post_id = graphene.Int(required=True) # ID of the post being liked.

    ok = graphene.Boolean() # Indicates successful like creation.


    def mutate(self, info, post_id):
        # Retrieves user and target post from context and database.
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Authentication required")
        post = Post.objects.get(id=post_id)
        
        # Ensures a like exists or creates one if necessary.
        Like.objects.get_or_create(user=user, post=post)

        return LikePost(ok=True)


# Root mutation class that exposes all defined mutations to the schema.
class Mutation(graphene.ObjectType):
    create_post = CreatePost.Field()
    add_comment = AddComment.Field()
    like_post = LikePost.Field()
