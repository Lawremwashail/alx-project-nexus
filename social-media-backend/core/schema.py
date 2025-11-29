import graphene
import graphql_jwt
from django.contrib.auth import get_user_model
from social.graphql.queries import Query as SocialQuery
from social.graphql.mutations import Mutation as SocialMutation
from social.graphql.types import UserType


User = get_user_model()


# The main Query class for the GraphQL schema.
# It inherits all fields/resolvers from the SocialQuery module
# and extends graphene.ObjectType (required by Graphene).

class Query(SocialQuery, graphene.ObjectType):
    # me returns a full UserType, not string
    me = graphene.Field(UserType, description="Return the authenticated user")

    def resolve_me(self, info):
        user = info.context.user
        if user.is_anonymous:
            return None
        return user
# The main Mutation class for GraphQL schema.
# It inherits all mutations from the SocialMutation module
# and extends graphene.ObjectType.

class Mutation(SocialMutation, graphene.ObjectType):
    # graphql_jwt provides tokenAuth, verify and refresh
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    # optionally: revoke/refresh token support:
    # revoke_token = graphql_jwt.relay.Revoke.Field()


# Create the GraphQL schema with the Query and Mutation root types.
schema = graphene.Schema(query=Query, mutation=Mutation)
