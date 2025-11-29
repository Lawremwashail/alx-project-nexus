import graphene
from django.contrib.auth import get_user_model
from graphql import GraphQLError
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class RegisterUser(graphene.Mutation):
    """
    Register a new user. Returns user id and username.
    """
    id = graphene.ID()
    username = graphene.String()
    email = graphene.String()

    class Arguments:
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    def mutate(self, info, username, email, password):
        # basic validation
        if User.objects.filter(username=username).exists():
            raise GraphQLError("Username already exists")
        if User.objects.filter(email=email).exists():
            raise GraphQLError("Email already exists")

        # optional: enforce password policy
        try:
            validate_password(password)
        except Exception as e:
            raise GraphQLError(f"Password validation error: {e}")

        user = User.objects.create_user(username=username, email=email, password=password)
        return RegisterUser(id=user.id, username=user.username, email=user.email)

