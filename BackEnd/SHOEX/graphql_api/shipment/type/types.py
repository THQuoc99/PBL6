import graphene
from graphene import relay
from graphene_django import DjangoObjectType

from shipments.models import Shipment, ShipmentTracking
from orders.models import Order

try:
    from graphql_api.order.Type.types import OrderType
except Exception:
    OrderType = None


class ShipmentTrackingType(DjangoObjectType):
    class Meta:
        model = ShipmentTracking
        fields = "__all__"
        interfaces = (relay.Node,)


class ShipmentType(DjangoObjectType):
    related_parties = graphene.JSONString()
    trackings = graphene.List(ShipmentTrackingType)
    user_orders = graphene.List(lambda: OrderType) if OrderType else graphene.List(graphene.String)

    class Meta:
        model = Shipment
        fields = "__all__"
        interfaces = (relay.Node,)

    def resolve_trackings(self, info):
        return self.trackings.all()

    def resolve_related_parties(self, info):
        try:
            buyer = None
            if hasattr(self, 'user') and self.user:
                buyer = {
                    'id': getattr(self.user, 'id', None) or getattr(self.user, 'pk', None),
                    'email': getattr(self.user, 'email', None),
                    'username': getattr(self.user, 'username', None),
                }

            store = None
            if hasattr(self, 'store') and self.store:
                store = {
                    'id': getattr(self.store, 'id', None) or getattr(self.store, 'pk', None),
                    'name': getattr(self.store, 'name', None),
                }

            sub_order = None
            if hasattr(self, 'sub_order') and self.sub_order:
                sub_order = {
                    'sub_order_id': getattr(self.sub_order, 'sub_order_id', None),
                    'store_id': getattr(self.sub_order.store, 'pk', None) if getattr(self.sub_order, 'store', None) else None,
                }

            return {
                'buyer': buyer,
                'store': store,
                'sub_order': sub_order,
                'tracking_code': getattr(self, 'tracking_code', None),
            }
        except Exception:
            return {}

    def resolve_user_orders(self, info):
        user = getattr(info.context, 'user', None)
        if not user or not getattr(user, 'is_authenticated', False):
            return []
        return Order.objects.filter(buyer=user).order_by('-created_at')
