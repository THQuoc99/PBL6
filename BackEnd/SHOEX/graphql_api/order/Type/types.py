import graphene
from graphene import relay
from graphene_django import DjangoObjectType

from orders.models import Order, SubOrder, OrderItem
try:
    from graphql_api.payment.types.types import PaymentType
except Exception:
    PaymentType = None

try:
    from graphql_api.shipment.type.types import ShipmentType
except Exception:
    ShipmentType = None


class OrderItemType(DjangoObjectType):
    class Meta:
        model = OrderItem
        fields = "__all__"
        interfaces = (relay.Node,)


class SubOrderType(DjangoObjectType):
    items = graphene.List(lambda: OrderItemType)
    shipment = graphene.Field(lambda: ShipmentType) if ShipmentType else graphene.String()

    class Meta:
        model = SubOrder
        fields = "__all__"
        interfaces = (relay.Node,)

    def resolve_items(self, info):
        return self.items.all()

    def resolve_shipment(self, info):
        # Shipment is a reverse OneToOne; return if exists
        try:
            return getattr(self, 'shipment', None)
        except Exception:
            return None


class OrderType(DjangoObjectType):
    sub_orders = graphene.List(lambda: SubOrderType)
    order_items = graphene.List(lambda: OrderItemType)
    payment = graphene.Field(lambda: PaymentType) if PaymentType else graphene.String()

    class Meta:
        model = Order
        fields = "__all__"
        interfaces = (relay.Node,)

    def resolve_sub_orders(self, info):
        return self.sub_orders.all()

    def resolve_order_items(self, info):
        return self.order_items.all()

    def resolve_payment(self, info):
        try:
            return getattr(self, 'payment', None)
        except Exception:
            return None
