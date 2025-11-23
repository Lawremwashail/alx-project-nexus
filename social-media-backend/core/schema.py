import graphene
from social.graphql.queries import Query as SocialQuery
from social.graphql.mutations import Mutation as SocialMutation

# The main Query class for the GraphQL schema.
# It inherits all fields/resolvers from the SocialQuery module
# and extends graphene.ObjectType (required by Graphene).

class Query(SocialQuery, graphene.ObjectType):
    pass

# The main Mutation class for GraphQL schema.
# It inherits all mutations from the SocialMutation module
# and extends graphene.ObjectType.

class Mutation(SocialMutation, graphene.ObjectType):
    pass

# Create the GraphQL schema with the Query and Mutation root types.
schema = graphene.Schema(query=Query, mutation=Mutation)
