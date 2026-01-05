# orders/graphql/inputs.py
import graphene
from decimal import Decimal

class OrderItemInput(graphene.InputObjectType):
    variant_id = graphene.ID(required=True)
    quantity = graphene.Int(required=True)
    price_at_order = graphene.Decimal(required=True)

class SubOrderInput(graphene.InputObjectType):
    store_id = graphene.ID(required=True)
    shipping_fee = graphene.Decimal(required=True)
    subtotal = graphene.Decimal(required=True)
    items = graphene.List(OrderItemInput, required=True)

class CreateOrderInput(graphene.InputObjectType):
    payment_method = graphene.String(required=True)
    address_id = graphene.ID(required=True)
    total_amount = graphene.Decimal(required=True)
    shipping_fee = graphene.Decimal(required=True)
    sub_orders = graphene.List(SubOrderInput, required=True)
