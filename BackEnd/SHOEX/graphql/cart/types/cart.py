import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from cart.models import Cart, CartItem, Wishlist
from decimal import Decimal


class CartType(DjangoObjectType):
    """Giỏ hàng của user"""
    class Meta:
        model = Cart
        fields = '__all__'
        interfaces = (relay.Node,)
    
    # Thêm các trường tùy chỉnh
    total_items = graphene.Int(description="Tổng số lượng sản phẩm trong giỏ hàng")
    total_amount = graphene.Decimal(description="Tổng giá trị giỏ hàng")
    total_weight = graphene.Decimal(description="Tổng khối lượng giỏ hàng")
    is_expired = graphene.Boolean(description="Giỏ hàng đã hết hạn chưa (cho guest)")
    
    def resolve_total_items(self, info):
        """Tổng số lượng sản phẩm trong giỏ hàng"""
        return self.total_items
    
    def resolve_total_amount(self, info):
        """Tổng giá trị giỏ hàng"""
        return self.total_amount
    
    def resolve_total_weight(self, info):
        """Tổng khối lượng giỏ hàng"""
        return self.total_weight
    
    def resolve_is_expired(self, info):
        """Kiểm tra giỏ hàng có hết hạn không"""
        if not self.expires_at:
            return False
        from django.utils import timezone
        return timezone.now() > self.expires_at


class CartItemType(DjangoObjectType):
    """Sản phẩm trong giỏ hàng"""
    class Meta:
        model = CartItem
        fields = '__all__'
        interfaces = (relay.Node,)
    
    # Thêm các trường tùy chỉnh
    subtotal = graphene.Decimal(description="Tổng tiền cho item này")
    current_price = graphene.Decimal(description="Giá hiện tại của sản phẩm")
    price_changed = graphene.Boolean(description="Giá có thay đổi so với lúc thêm vào giỏ không")
    is_available = graphene.Boolean(description="Sản phẩm còn có sẵn không")
    max_quantity = graphene.Int(description="Số lượng tối đa có thể đặt")
    
    def resolve_subtotal(self, info):
        """Tính tổng tiền cho item này"""
        return self.subtotal
    
    def resolve_current_price(self, info):
        """Giá hiện tại của sản phẩm"""
        return self.current_price
    
    def resolve_price_changed(self, info):
        """Kiểm tra giá có thay đổi không"""
        return self.price_changed
    
    def resolve_is_available(self, info):
        """Kiểm tra sản phẩm còn có sẵn không"""
        return (
            self.variant.is_active and 
            self.variant.product.is_active and 
            self.variant.stock > 0
        )
    
    def resolve_max_quantity(self, info):
        """Số lượng tối đa có thể đặt"""
        return self.variant.stock


class WishlistType(DjangoObjectType):
    """Sản phẩm trong wishlist"""
    class Meta:
        model = Wishlist
        fields = '__all__'
        interfaces = (relay.Node,)
    
    # Thêm các trường tùy chỉnh
    is_available = graphene.Boolean(description="Sản phẩm còn có sẵn không")
    current_price = graphene.Decimal(description="Giá hiện tại của sản phẩm")
    is_in_stock = graphene.Boolean(description="Còn hàng hay không")
    
    def resolve_is_available(self, info):
        """Kiểm tra sản phẩm còn có sẵn không"""
        return (
            self.variant.is_active and 
            self.variant.product.is_active
        )
    
    def resolve_current_price(self, info):
        """Giá hiện tại của sản phẩm"""
        return self.variant.price
    
    def resolve_is_in_stock(self, info):
        """Kiểm tra còn hàng không"""
        return self.variant.stock > 0


# ===== CONNECTION TYPES =====
class CartConnection(relay.Connection):
    class Meta:
        node = CartType


class CartItemConnection(relay.Connection):
    class Meta:
        node = CartItemType


class WishlistConnection(relay.Connection):
    class Meta:
        node = WishlistType


# ===== INPUT TYPES =====
class CartItemInput(graphene.InputObjectType):
    """Input để thêm/cập nhật sản phẩm vào giỏ hàng"""
    variant_id = graphene.ID(required=True, description="ID của variant sản phẩm")
    quantity = graphene.Int(required=True, description="Số lượng")


class CartUpdateInput(graphene.InputObjectType):
    """Input để cập nhật giỏ hàng"""
    session_key = graphene.String(description="Session key cho guest user")


class WishlistItemInput(graphene.InputObjectType):
    """Input để thêm sản phẩm vào wishlist"""
    variant_id = graphene.ID(required=True, description="ID của variant sản phẩm")


# ===== ENUM TYPES =====
class CartSortField(graphene.Enum):
    """Các trường để sắp xếp giỏ hàng"""
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    TOTAL_AMOUNT = "total_amount"
    TOTAL_ITEMS = "total_items"


class CartItemSortField(graphene.Enum):
    """Các trường để sắp xếp items trong giỏ hàng"""
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    UNIT_PRICE = "unit_price"
    QUANTITY = "quantity"
    SUBTOTAL = "subtotal"


class WishlistSortField(graphene.Enum):
    """Các trường để sắp xếp wishlist"""
    CREATED_AT = "created_at"
    PRODUCT_NAME = "variant__product__name"
    PRICE = "variant__price"


# ===== SUMMARY TYPES =====
class CartSummary(graphene.ObjectType):
    """Tóm tắt thông tin giỏ hàng"""
    total_items = graphene.Int(description="Tổng số lượng sản phẩm")
    total_amount = graphene.Decimal(description="Tổng giá trị")
    total_weight = graphene.Decimal(description="Tổng khối lượng")
    item_count = graphene.Int(description="Số loại sản phẩm khác nhau")
    has_unavailable_items = graphene.Boolean(description="Có sản phẩm không còn bán không")
    has_price_changes = graphene.Boolean(description="Có sản phẩm thay đổi giá không")


class WishlistSummary(graphene.ObjectType):
    """Tóm tắt thông tin wishlist"""
    total_items = graphene.Int(description="Tổng số sản phẩm trong wishlist")
    available_items = graphene.Int(description="Số sản phẩm còn có sẵn")
    unavailable_items = graphene.Int(description="Số sản phẩm không còn bán")
    in_stock_items = graphene.Int(description="Số sản phẩm còn hàng")
    out_of_stock_items = graphene.Int(description="Số sản phẩm hết hàng")