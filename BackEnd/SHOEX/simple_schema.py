import graphene

class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hello SHOEX GraphQL!")

schema = graphene.Schema(query=Query)