import graphene
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from graphql import GraphQLError
from django.contrib.auth.password_validation import validate_password
import graphql_jwt
from .types import UserType

User = get_user_model()


# --------------------------------------------------
# REGISTER USER
# --------------------------------------------------
class RegisterUser(graphene.Mutation):
    user = graphene.Field(UserType)
    ok = graphene.Boolean()

    class Arguments:
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    def mutate(self, info, username, email, password):
        if User.objects.filter(username=username).exists():
            raise GraphQLError("Username already exists")

        if User.objects.filter(email=email).exists():
            raise GraphQLError("Email already exists")

        validate_password(password)

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        return RegisterUser(user=user, ok=True)


# --------------------------------------------------
# LOGIN USER
# --------------------------------------------------
class LoginUser(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    token = graphene.String()
    user = graphene.Field(UserType)

    def mutate(self, info, email, password):
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise GraphQLError("Invalid credentials")

        if not user.check_password(password):
            raise GraphQLError("Invalid credentials")

        # Use graphql_jwt library to create token
        payload = graphql_jwt.utils.jwt_payload(user)
        token = graphql_jwt.utils.jwt_encode(payload)

        return LoginUser(user=user, token=token)
