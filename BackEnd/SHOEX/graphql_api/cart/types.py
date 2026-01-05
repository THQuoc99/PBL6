import graphene
from graphene_django import DjangoObjectType
from graphene import relay
from cart.models import Cart, CartItem


class CartItemType(DjangoObjectType):
    """GraphQL Type cho CartItem"""
    subtotal = graphene.Decimal(description="Thành tiền (số lượng * đơn giá)")
    
    class Meta:
        model = CartItem
        fields = "__all__"
        interfaces = (relay.Node,)
    



class CartType(DjangoObjectType):
    """GraphQL Type cho Cart"""
    items = graphene.List(CartItemType, description="Danh sách sản phẩm trong giỏ hàng")
    total_items = graphene.Int(description="Tổng số sản phẩm khác nhau")
    total_amount = graphene.Decimal(description="Tổng giá trị giỏ hàng")
    total_weight = graphene.Decimal(description="Tổng khối lượng (để tính ship)")
    
    class Meta:
        model = Cart
        fields = "__all__"
        interfaces = (relay.Node,)
    
    def resolve_items(self, info):
        return self.items.select_related('variant__product').all()
    
    def resolve_total_items(self, info):
        return self.total_items
    
    def resolve_total_amount(self, info):
        return self.total_amount
    
    def resolve_total_weight(self, info):
        return self.total_weight


class CartCountableConnection(relay.Connection):
    """Connection cho pagination Cart"""
    class Meta:
        node = CartType
