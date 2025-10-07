import graphene
from graphene import InputObjectType, Mutation
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from cart.models import Cart, CartItem, Wishlist
from products.models import ProductVariant
from ..types.cart import CartType, CartItemType, WishlistType, CartItemInput, WishlistItemInput

User = get_user_model()


# ===== CART MUTATIONS =====

class AddToCart(Mutation):
    """Thêm sản phẩm vào giỏ hàng"""
    
    class Arguments:
        input = CartItemInput(required=True)
        session_key = graphene.String(description="Session key cho guest user")
    
    success = graphene.Boolean()
    cart_item = graphene.Field(CartItemType)
    cart = graphene.Field(CartType)
    errors = graphene.List(graphene.String)
    
    def mutate(self, info, input, session_key=None):
        user = info.context.user
        errors = []
        
        try:
            # Lấy variant
            try:
                variant = ProductVariant.objects.get(
                    variant_id=input.variant_id,
                    is_active=True,
                    product__is_active=True
                )
            except ProductVariant.DoesNotExist:
                return AddToCart(
                    success=False,
                    errors=["Product variant not found or inactive"]
                )
            
            # Kiểm tra tồn kho
            if input.quantity > variant.stock:
                return AddToCart(
                    success=False,
                    errors=[f"Insufficient stock. Available: {variant.stock}"]
                )
            
            # Lấy hoặc tạo cart
            if user.is_authenticated:
                cart, created = Cart.objects.get_or_create(user=user)
            elif session_key:
                cart, created = Cart.objects.get_or_create(
                    session_key=session_key,
                    defaults={
                        'expires_at': timezone.now() + timezone.timedelta(days=30)
                    }
                )
            else:
                return AddToCart(
                    success=False,
                    errors=["Session key required for guest user"]
                )
            
            # Thêm hoặc cập nhật cart item
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                variant=variant,
                defaults={
                    'quantity': input.quantity,
                    'unit_price': variant.price
                }
            )
            
            if not created:
                # Cập nhật số lượng nếu đã có
                new_quantity = cart_item.quantity + input.quantity
                if new_quantity > variant.stock:
                    return AddToCart(
                        success=False,
                        errors=[f"Total quantity would exceed stock. Available: {variant.stock}"]
                    )
                cart_item.quantity = new_quantity
                cart_item.save()
            
            return AddToCart(
                success=True,
                cart_item=cart_item,
                cart=cart
            )
            
        except Exception as e:
            return AddToCart(
                success=False,
                errors=[str(e)]
            )


class UpdateCartItem(Mutation):
    """Cập nhật số lượng sản phẩm trong giỏ hàng"""
    
    class Arguments:
        item_id = graphene.ID(required=True)
        quantity = graphene.Int(required=True)
    
    success = graphene.Boolean()
    cart_item = graphene.Field(CartItemType)
    errors = graphene.List(graphene.String)
    
    def mutate(self, info, item_id, quantity):
        user = info.context.user
        
        try:
            # Lấy cart item
            if user.is_authenticated:
                cart_item = CartItem.objects.get(
                    item_id=item_id,
                    cart__user=user
                )
            else:
                session_key = info.context.session.session_key
                cart_item = CartItem.objects.get(
                    item_id=item_id,
                    cart__session_key=session_key
                )
            
            # Kiểm tra tồn kho
            if quantity > cart_item.variant.stock:
                return UpdateCartItem(
                    success=False,
                    errors=[f"Insufficient stock. Available: {cart_item.variant.stock}"]
                )
            
            if quantity <= 0:
                # Xóa item nếu quantity <= 0
                cart_item.delete()
                return UpdateCartItem(success=True)
            
            # Cập nhật số lượng
            cart_item.quantity = quantity
            cart_item.save()
            
            return UpdateCartItem(
                success=True,
                cart_item=cart_item
            )
            
        except CartItem.DoesNotExist:
            return UpdateCartItem(
                success=False,
                errors=["Cart item not found"]
            )
        except Exception as e:
            return UpdateCartItem(
                success=False,
                errors=[str(e)]
            )


class RemoveFromCart(Mutation):
    """Xóa sản phẩm khỏi giỏ hàng"""
    
    class Arguments:
        item_id = graphene.ID(required=True)
    
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)
    
    def mutate(self, info, item_id):
        user = info.context.user
        
        try:
            # Lấy cart item
            if user.is_authenticated:
                cart_item = CartItem.objects.get(
                    item_id=item_id,
                    cart__user=user
                )
            else:
                session_key = info.context.session.session_key
                cart_item = CartItem.objects.get(
                    item_id=item_id,
                    cart__session_key=session_key
                )
            
            cart_item.delete()
            
            return RemoveFromCart(success=True)
            
        except CartItem.DoesNotExist:
            return RemoveFromCart(
                success=False,
                errors=["Cart item not found"]
            )
        except Exception as e:
            return RemoveFromCart(
                success=False,
                errors=[str(e)]
            )


class ClearCart(Mutation):
    """Xóa tất cả sản phẩm trong giỏ hàng"""
    
    class Arguments:
        session_key = graphene.String(description="Session key cho guest user")
    
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)
    
    def mutate(self, info, session_key=None):
        user = info.context.user
        
        try:
            # Lấy cart
            if user.is_authenticated:
                cart = Cart.objects.get(user=user)
            elif session_key:
                cart = Cart.objects.get(session_key=session_key)
            else:
                return ClearCart(
                    success=False,
                    errors=["Session key required for guest user"]
                )
            
            cart.clear()
            
            return ClearCart(success=True)
            
        except Cart.DoesNotExist:
            return ClearCart(
                success=False,
                errors=["Cart not found"]
            )
        except Exception as e:
            return ClearCart(
                success=False,
                errors=[str(e)]
            )


class MergeCart(Mutation):
    """Gộp giỏ hàng guest vào user cart khi login"""
    
    class Arguments:
        session_key = graphene.String(required=True)
    
    success = graphene.Boolean()
    cart = graphene.Field(CartType)
    errors = graphene.List(graphene.String)
    
    def mutate(self, info, session_key):
        user = info.context.user
        
        if not user.is_authenticated:
            return MergeCart(
                success=False,
                errors=["Authentication required"]
            )
        
        try:
            # Lấy guest cart
            guest_cart = Cart.objects.get(session_key=session_key)
            
            # Lấy hoặc tạo user cart
            user_cart, created = Cart.objects.get_or_create(user=user)
            
            # Gộp giỏ hàng
            user_cart.merge_cart(guest_cart)
            
            return MergeCart(
                success=True,
                cart=user_cart
            )
            
        except Cart.DoesNotExist:
            return MergeCart(
                success=False,
                errors=["Guest cart not found"]
            )
        except Exception as e:
            return MergeCart(
                success=False,
                errors=[str(e)]
            )


# ===== WISHLIST MUTATIONS =====

class AddToWishlist(Mutation):
    """Thêm sản phẩm vào wishlist"""
    
    class Arguments:
        input = WishlistItemInput(required=True)
    
    success = graphene.Boolean()
    wishlist_item = graphene.Field(WishlistType)
    errors = graphene.List(graphene.String)
    
    def mutate(self, info, input):
        user = info.context.user
        
        if not user.is_authenticated:
            return AddToWishlist(
                success=False,
                errors=["Authentication required"]
            )
        
        try:
            # Lấy variant
            try:
                variant = ProductVariant.objects.get(
                    variant_id=input.variant_id,
                    is_active=True,
                    product__is_active=True
                )
            except ProductVariant.DoesNotExist:
                return AddToWishlist(
                    success=False,
                    errors=["Product variant not found or inactive"]
                )
            
            # Tạo wishlist item
            wishlist_item, created = Wishlist.objects.get_or_create(
                user=user,
                variant=variant
            )
            
            if not created:
                return AddToWishlist(
                    success=False,
                    errors=["Product already in wishlist"]
                )
            
            return AddToWishlist(
                success=True,
                wishlist_item=wishlist_item
            )
            
        except Exception as e:
            return AddToWishlist(
                success=False,
                errors=[str(e)]
            )


class RemoveFromWishlist(Mutation):
    """Xóa sản phẩm khỏi wishlist"""
    
    class Arguments:
        wishlist_id = graphene.ID(required=True)
    
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)
    
    def mutate(self, info, wishlist_id):
        user = info.context.user
        
        if not user.is_authenticated:
            return RemoveFromWishlist(
                success=False,
                errors=["Authentication required"]
            )
        
        try:
            wishlist_item = Wishlist.objects.get(
                wishlist_id=wishlist_id,
                user=user
            )
            
            wishlist_item.delete()
            
            return RemoveFromWishlist(success=True)
            
        except Wishlist.DoesNotExist:
            return RemoveFromWishlist(
                success=False,
                errors=["Wishlist item not found"]
            )
        except Exception as e:
            return RemoveFromWishlist(
                success=False,
                errors=[str(e)]
            )


class MoveToCartFromWishlist(Mutation):
    """Chuyển sản phẩm từ wishlist vào giỏ hàng"""
    
    class Arguments:
        wishlist_id = graphene.ID(required=True)
        quantity = graphene.Int(default_value=1)
    
    success = graphene.Boolean()
    cart_item = graphene.Field(CartItemType)
    errors = graphene.List(graphene.String)
    
    def mutate(self, info, wishlist_id, quantity=1):
        user = info.context.user
        
        if not user.is_authenticated:
            return MoveToCartFromWishlist(
                success=False,
                errors=["Authentication required"]
            )
        
        try:
            wishlist_item = Wishlist.objects.get(
                wishlist_id=wishlist_id,
                user=user
            )
            
            # Kiểm tra tồn kho
            if quantity > wishlist_item.variant.stock:
                return MoveToCartFromWishlist(
                    success=False,
                    errors=[f"Insufficient stock. Available: {wishlist_item.variant.stock}"]
                )
            
            # Chuyển vào giỏ hàng
            cart, created = Cart.objects.get_or_create(user=user)
            
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                variant=wishlist_item.variant,
                defaults={
                    'quantity': quantity,
                    'unit_price': wishlist_item.variant.price
                }
            )
            
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            
            # Xóa khỏi wishlist
            wishlist_item.delete()
            
            return MoveToCartFromWishlist(
                success=True,
                cart_item=cart_item
            )
            
        except Wishlist.DoesNotExist:
            return MoveToCartFromWishlist(
                success=False,
                errors=["Wishlist item not found"]
            )
        except Exception as e:
            return MoveToCartFromWishlist(
                success=False,
                errors=[str(e)]
            )


class ClearWishlist(Mutation):
    """Xóa tất cả sản phẩm trong wishlist"""
    
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)
    
    def mutate(self, info):
        user = info.context.user
        
        if not user.is_authenticated:
            return ClearWishlist(
                success=False,
                errors=["Authentication required"]
            )
        
        try:
            user.wishlist_items.all().delete()
            
            return ClearWishlist(success=True)
            
        except Exception as e:
            return ClearWishlist(
                success=False,
                errors=[str(e)]
            )