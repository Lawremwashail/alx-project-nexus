from django.test import TestCase
from django.contrib.auth import get_user_model
from graphene.test import Client
from core.schema import schema

User = get_user_model()

class AuthGraphQLTests(TestCase):
    def setUp(self):
        self.client = Client(schema)
        self.user = User.objects.create_user(username="u1", email="u1@example.com", password="pass123")

    def test_register_user(self):
        q = '''
        mutation {
          registerUser(username:"newuser", email:"a@b.com", password:"strongPassword123") {
            id
            username
          }
        }
        '''
        res = self.client.execute(q)
        assert res.get("errors") is None
        data = res["data"]["registerUser"]
        self.assertEqual(data["username"], "newuser")

    def test_token_auth(self):
        q = '''
        mutation {
          tokenAuth(username:"u1", password:"pass123") {
            token
            user {
              username
            }
          }
        }
        '''
        res = self.client.execute(q)
        assert res.get("errors") is None
        token = res["data"]["tokenAuth"]["token"]
        self.assertIsNotNone(token)

