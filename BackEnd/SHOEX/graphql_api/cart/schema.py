import graphene
from graphene import relay
from django.db.models import Q
from cart.models import Cart, CartItem
from .types import CartType, CartItemType, CartCountableConnection


class CartQueries(graphene.ObjectType):
    """Queries cho Cart"""
    
    # Single cart query
    my_cart = graphene.Field(
        CartType,
        description="Lấy giỏ hàng của user hiện tại"
    )
    
    # Cart items
    cart_items = graphene.List(
        CartItemType,
        description="Lấy danh sách items trong giỏ hàng"
    )
    
    def resolve_my_cart(self, info):
        """Lấy giỏ hàng của user hiện tại"""
        user = info.context.user
        
        if not user or not user.is_authenticated:
            return None
        
        try:
            cart = Cart.objects.get(user=user)
            return cart
        except Cart.DoesNotExist:
            # Tạo cart mới nếu chưa có
            cart = Cart.objects.create(user=user)
            return cart
    
    def resolve_cart_items(self, info):
        """Lấy danh sách items trong giỏ hàng"""
        user = info.context.user
        
        if not user or not user.is_authenticated:
            return []
        
        try:
            cart = Cart.objects.get(user=user)
            return cart.items.select_related(
                'variant__product',
                'variant__color',
                'variant__size'
            ).all()
        except Cart.DoesNotExist:
            return []


class CartMutations(graphene.ObjectType):
    """Mutations cho Cart"""
    
    from .mutations.mutations import (
        AddToCart,
        RemoveFromCart,
        UpdateCartItemQuantity,
        ClearCart
    )
    
    # Add to cart
    add_to_cart = AddToCart.Field(description="Thêm sản phẩm vào giỏ hàng")
    
    # Remove from cart
    remove_from_cart = RemoveFromCart.Field(description="Xóa sản phẩm khỏi giỏ hàng")
    
    # Update quantity
    update_cart_item_quantity = UpdateCartItemQuantity.Field(
        description="Cập nhật số lượng sản phẩm trong giỏ hàng"
    )
    
    # Clear cart
    clear_cart = ClearCart.Field(description="Xóa tất cả sản phẩm trong giỏ hàng")
