from django.test import TestCase
from django.contrib.auth import get_user_model
from graphene.test import Client
from social.schema import schema
from social.models import Post, Comment, Like, Follow, Notification

User = get_user_model()


class MutationTests(TestCase):

    def setUp(self):
        # GraphQL client
        self.client = Client(schema)

        # Create a test user
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )

        # Create another user for follow tests
        self.other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="password123"
        )

        # Authenticate the user
        self.client.context = self.get_context()

    def get_context(self):
        """
        Generates a dummy request-like context with the logged-in user.
        """
        class DummyContext:
            user = self.user
        return DummyContext()

    # -----------------------------------
    # Test CreatePost Mutation
    # -----------------------------------
    def test_create_post(self):
        query = '''
            mutation {
              createPost(content: "Hello World") {
                post {
                  id
                  content
                }
              }
            }
        '''

        response = self.client.execute(query)

        post_data = response["data"]["createPost"]["post"]

        self.assertIsNotNone(post_data["id"])
        self.assertEqual(post_data["content"], "Hello World")

        # Check database
        self.assertEqual(Post.objects.count(), 1)

    # -----------------------------------
    # Test addComment Mutation
    # -----------------------------------
    def test_add_comment(self):
        post = Post.objects.create(author=self.user, content="Test Post")

        query = f'''
            mutation {{
              addComment(postId: {post.id}, content: "Nice post!") {{
                comment {{
                  id
                  content
                  post {{
                    id
                  }}
                }}
              }}
            }}
        '''

        response = self.client.execute(query)
        comment_data = response["data"]["addComment"]["comment"]

        self.assertIsNotNone(comment_data["id"])
        self.assertEqual(comment_data["content"], "Nice post!")
        self.assertEqual(int(comment_data["post"]["id"]), post.id)

        # Check database
        self.assertEqual(Comment.objects.count(), 1)

    # -----------------------------------
    # Test likePost Mutation
    # -----------------------------------
    def test_like_post(self):
        post = Post.objects.create(author=self.user, content="Test Post")

        query = f'''
            mutation {{
              likePost(postId: {post.id}) {{
                ok
              }}
            }}
        '''

        response = self.client.execute(query)

        self.assertTrue(response["data"]["likePost"]["ok"])

        # Check database
        self.assertEqual(Like.objects.count(), 1)

    # -----------------------------------
    # Liking twice does not create duplicates
    # -----------------------------------
    def test_like_post_idempotent(self):
        post = Post.objects.create(author=self.user, content="Test Post")

        query = f'''
            mutation {{
              likePost(postId: {post.id}) {{
                ok
              }}
            }}
        '''

        # First like
        self.client.execute(query)
        # Second like should not create duplicate
        self.client.execute(query)

        # Still only one like
        self.assertEqual(Like.objects.count(), 1)

    # -----------------------------------
    # Test followUser Mutation
    # -----------------------------------
    def test_follow_user(self):
        query = f'''
            mutation {{
              followUser(userId: {self.other_user.id}) {{
                ok
              }}
            }}
        '''

        response = self.client.execute(query)
        self.assertTrue(response["data"]["followUser"]["ok"])
        self.assertEqual(self.user.following.count(), 1)

    # -----------------------------------
    # Test createNotification Mutation
    # -----------------------------------
    def test_create_notification(self):
        query = '''
            mutation {
              createNotification(userId: 1, message: "Test notification") {
                notification {
                  id
                  message
                }
              }
            }
        '''

        response = self.client.execute(query)
        notif = response["data"]["createNotification"]["notification"]

        self.assertIsNotNone(notif["id"])
        self.assertEqual(notif["message"], "Test notification")
        self.assertEqual(Notification.objects.count(), 1)

