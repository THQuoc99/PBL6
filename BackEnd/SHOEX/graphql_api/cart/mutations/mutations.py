import graphene
from graphene import relay
from django.db import transaction
from django.core.exceptions import ValidationError
from cart.models import Cart, CartItem
from products.models import ProductVariant
from ..types import CartType, CartItemType


class AddToCart(relay.ClientIDMutation):
    """Thêm sản phẩm vào giỏ hàng"""
    
    class Input:
        variant_id = graphene.ID(required=True, description="ID của variant sản phẩm")
        quantity = graphene.Int(required=True, description="Số lượng")
    
    cart = graphene.Field(CartType)
    cart_item = graphene.Field(CartItemType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)
    
    @classmethod
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info, **input):
        variant_id = input.get('variant_id')
        quantity = input.get('quantity', 1)
        
        errors = []
        
        # Validate quantity
        if quantity <= 0:
            return AddToCart(
                success=False,
                errors=["Số lượng phải lớn hơn 0"]
            )
        
        try:
            # Lấy user từ context (đã được authenticate bởi JWT middleware)
            user = info.context.user
            
            # Kiểm tra user đã đăng nhập chưa
            if not user or not user.is_authenticated:
                return AddToCart(
                    success=False,
                    errors=["Vui lòng đăng nhập để thêm sản phẩm vào giỏ hàng"]
                )
            
            # Tạo hoặc lấy cart của user
            cart, created = Cart.objects.get_or_create(
                user=user,
                session_key=None  # User cart không cần session_key
            )
            
            # Get variant
            try:
                variant = ProductVariant.objects.select_related('product').get(variant_id=variant_id)
            except ProductVariant.DoesNotExist:
                return AddToCart(
                    success=False,
                    errors=["Sản phẩm không tồn tại"]
                )
            
            # Check if variant is active
            if not variant.is_active:
                return AddToCart(
                    success=False,
                    errors=["Sản phẩm không còn bán"]
                )
            
            # Check stock
            if variant.stock < quantity:
                return AddToCart(
                    success=False,
                    errors=[f"Chỉ còn {variant.stock} sản phẩm trong kho"]
                )
            
            # Check if item already exists in cart
            cart_item, item_created = CartItem.objects.get_or_create(
                cart=cart,
                variant=variant,
                defaults={
                    'quantity': quantity,
                    'unit_price': variant.price
                }
            )
            
            if not item_created:
                # Update quantity if item already exists
                new_quantity = cart_item.quantity + quantity
                
                # Check stock again
                if variant.stock < new_quantity:
                    return AddToCart(
                        success=False,
                        errors=[f"Chỉ còn {variant.stock} sản phẩm trong kho"]
                    )
                
                cart_item.quantity = new_quantity
                cart_item.unit_price = variant.price
                cart_item.save()
            
            return AddToCart(
                cart=cart,
                cart_item=cart_item,
                success=True,
                errors=[]
            )
            
        except Exception as e:
            return AddToCart(
                success=False,
                errors=[str(e)]
            )


class RemoveFromCart(relay.ClientIDMutation):
    """Xóa sản phẩm khỏi giỏ hàng"""
    
    class Input:
        item_id = graphene.ID(required=True, description="ID của cart item")
    
    cart = graphene.Field(CartType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)
    
    @classmethod
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info, **input):
        item_id = input.get('item_id')
        
        try:
            # Lấy user từ context
            user = info.context.user
            if not user or not user.is_authenticated:
                return RemoveFromCart(
                    success=False,
                    errors=["Vui lòng đăng nhập"]
                )
            
            # Get cart item của user
            cart_item = CartItem.objects.select_related('cart').get(
                item_id=item_id,
                cart__user=user
            )
            
            cart = cart_item.cart
            cart_item.delete()
            
            return RemoveFromCart(
                cart=cart,
                success=True,
                errors=[]
            )
            
        except CartItem.DoesNotExist:
            return RemoveFromCart(
                success=False,
                errors=["Sản phẩm không tồn tại trong giỏ hàng"]
            )
        except Exception as e:
            return RemoveFromCart(
                success=False,
                errors=[str(e)]
            )


class UpdateCartItemQuantity(relay.ClientIDMutation):
    """Cập nhật số lượng sản phẩm trong giỏ hàng"""
    
    class Input:
        item_id = graphene.ID(required=True, description="ID của cart item")
        quantity = graphene.Int(required=True, description="Số lượng mới")
    
    cart_item = graphene.Field(CartItemType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)
    
    @classmethod
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info, **input):
        item_id = input.get('item_id')
        quantity = input.get('quantity')
        
        # Validate quantity
        if quantity <= 0:
            return UpdateCartItemQuantity(
                success=False,
                errors=["Số lượng phải lớn hơn 0"]
            )
        
        try:
            # Lấy user từ context
            user = info.context.user
            if not user or not user.is_authenticated:
                return UpdateCartItemQuantity(
                    success=False,
                    errors=["Vui lòng đăng nhập"]
                )
            
            # Get cart item của user
            cart_item = CartItem.objects.select_related('cart', 'variant').get(
                item_id=item_id,
                cart__user=user
            )
            
            # Check stock
            if cart_item.variant.stock < quantity:
                return UpdateCartItemQuantity(
                    success=False,
                    errors=[f"Chỉ còn {cart_item.variant.stock} sản phẩm trong kho"]
                )
            
            # Update quantity and price
            cart_item.quantity = quantity
            cart_item.unit_price = cart_item.variant.price
            cart_item.save()
            
            return UpdateCartItemQuantity(
                cart_item=cart_item,
                success=True,
                errors=[]
            )
            
        except CartItem.DoesNotExist:
            return UpdateCartItemQuantity(
                success=False,
                errors=["Sản phẩm không tồn tại trong giỏ hàng"]
            )
        except Exception as e:
            return UpdateCartItemQuantity(
                success=False,
                errors=[str(e)]
            )


class ClearCart(relay.ClientIDMutation):
    """Xóa tất cả sản phẩm trong giỏ hàng"""
    
    class Input:
        pass
    
    cart = graphene.Field(CartType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)
    
    @classmethod
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info, **input):
        try:
            # Lấy user từ context
            user = info.context.user
            if not user or not user.is_authenticated:
                return ClearCart(
                    success=False,
                    errors=["Vui lòng đăng nhập"]
                )
            
            # Get cart của user
            cart = Cart.objects.get(user=user)
            cart.clear()
            
            return ClearCart(
                cart=cart,
                success=True,
                errors=[]
            )
            
        except Cart.DoesNotExist:
            return ClearCart(
                success=False,
                errors=["Giỏ hàng không tồn tại"]
            )
        except Exception as e:
            return ClearCart(
                success=False,
                errors=[str(e)]
            )
