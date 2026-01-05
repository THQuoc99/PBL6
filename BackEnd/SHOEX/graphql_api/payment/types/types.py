import graphene
from graphene import relay
from graphene_django import DjangoObjectType

from payments.models import Payment

try:
    from graphql_api.order.Type.types import OrderType
except Exception:
    OrderType = None


class PaymentType(DjangoObjectType):
    order = graphene.Field(lambda: OrderType) if OrderType else graphene.String()

    class Meta:
        model = Payment
        fields = "__all__"
        interfaces = (relay.Node,)

    def resolve_order(self, info):
        try:
            return self.order
        except Exception:
            return None
