import graphene
from graphene import InputObjectType
from django_filters import FilterSet, CharFilter, NumberFilter, BooleanFilter, OrderingFilter, DateTimeFilter
from django.db import models
from django.db.models import Q, Count, Sum, F
from django.utils import timezone
from cart.models import Cart, CartItem, Wishlist


class CartFilterSet(FilterSet):
    """Django FilterSet cho Cart model"""
    
    # Lọc theo user
    user = NumberFilter(field_name='user_id')
    session_key = CharFilter(field_name='session_key')
    
    # Lọc theo thời gian
    created_after = DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    # Lọc theo trạng thái
    is_expired = BooleanFilter(method='filter_is_expired')
    has_items = BooleanFilter(method='filter_has_items')
    
    # Lọc theo giá trị
    total_amount_min = NumberFilter(method='filter_total_amount_min')
    total_amount_max = NumberFilter(method='filter_total_amount_max')
    
    # Sắp xếp
    order_by = OrderingFilter(
        fields=(
            ('created_at', 'created_at'),
            ('updated_at', 'updated_at'),
        )
    )
    
    class Meta:
        model = Cart
        fields = ['user', 'session_key']
    
    def filter_is_expired(self, queryset, name, value):
        """Lọc cart đã hết hạn"""
        now = timezone.now()
        if value:
            return queryset.filter(expires_at__lt=now)
        else:
            return queryset.filter(Q(expires_at__isnull=True) | Q(expires_at__gte=now))
    
    def filter_has_items(self, queryset, name, value):
        """Lọc cart có items hay không"""
        if value:
            return queryset.annotate(item_count=Count('items')).filter(item_count__gt=0)
        else:
            return queryset.annotate(item_count=Count('items')).filter(item_count=0)
    
    def filter_total_amount_min(self, queryset, name, value):
        """Lọc theo tổng giá trị tối thiểu"""
        # Cần tính toán total_amount từ các items
        return queryset.annotate(
            total=Sum(F('items__quantity') * F('items__unit_price'))
        ).filter(total__gte=value)
    
    def filter_total_amount_max(self, queryset, name, value):
        """Lọc theo tổng giá trị tối đa"""
        return queryset.annotate(
            total=Sum(F('items__quantity') * F('items__unit_price'))
        ).filter(total__lte=value)


class CartItemFilterSet(FilterSet):
    """Django FilterSet cho CartItem model"""
    
    # Lọc theo cart
    cart = NumberFilter(field_name='cart_id')
    cart_user = NumberFilter(field_name='cart__user_id')
    
    # Lọc theo variant
    variant = NumberFilter(field_name='variant_id')
    product = NumberFilter(field_name='variant__product_id')
    category = NumberFilter(field_name='variant__product__category_id')
    
    # Lọc theo giá
    unit_price_min = NumberFilter(field_name='unit_price', lookup_expr='gte')
    unit_price_max = NumberFilter(field_name='unit_price', lookup_expr='lte')
    
    # Lọc theo số lượng
    quantity_min = NumberFilter(field_name='quantity', lookup_expr='gte')
    quantity_max = NumberFilter(field_name='quantity', lookup_expr='lte')
    
    # Lọc theo trạng thái
    price_changed = BooleanFilter(method='filter_price_changed')
    is_available = BooleanFilter(method='filter_is_available')
    
    # Sắp xếp
    order_by = OrderingFilter(
        fields=(
            ('created_at', 'created_at'),
            ('updated_at', 'updated_at'),
            ('unit_price', 'unit_price'),
            ('quantity', 'quantity'),
        )
    )
    
    class Meta:
        model = CartItem
        fields = ['cart', 'variant']
    
    def filter_price_changed(self, queryset, name, value):
        """Lọc items có giá thay đổi"""
        if value:
            return queryset.filter(~Q(unit_price=F('variant__price')))
        else:
            return queryset.filter(unit_price=F('variant__price'))
    
    def filter_is_available(self, queryset, name, value):
        """Lọc items còn có sẵn"""
        if value:
            return queryset.filter(
                variant__is_active=True,
                variant__product__is_active=True,
                variant__stock__gt=0
            )
        else:
            return queryset.filter(
                Q(variant__is_active=False) |
                Q(variant__product__is_active=False) |
                Q(variant__stock=0)
            )


class WishlistFilterSet(FilterSet):
    """Django FilterSet cho Wishlist model"""
    
    # Lọc theo user
    user = NumberFilter(field_name='user_id')
    
    # Lọc theo variant
    variant = NumberFilter(field_name='variant_id')
    product = NumberFilter(field_name='variant__product_id')
    category = NumberFilter(field_name='variant__product__category_id')
    
    # Lọc theo thời gian
    created_after = DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    # Lọc theo trạng thái
    is_available = BooleanFilter(method='filter_is_available')
    is_in_stock = BooleanFilter(method='filter_is_in_stock')
    
    # Sắp xếp
    order_by = OrderingFilter(
        fields=(
            ('created_at', 'created_at'),
            ('variant__product__name', 'product_name'),
            ('variant__price', 'price'),
        )
    )
    
    class Meta:
        model = Wishlist
        fields = ['user', 'variant']
    
    def filter_is_available(self, queryset, name, value):
        """Lọc items còn có sẵn"""
        if value:
            return queryset.filter(
                variant__is_active=True,
                variant__product__is_active=True
            )
        else:
            return queryset.filter(
                Q(variant__is_active=False) |
                Q(variant__product__is_active=False)
            )
    
    def filter_is_in_stock(self, queryset, name, value):
        """Lọc items còn hàng"""
        if value:
            return queryset.filter(variant__stock__gt=0)
        else:
            return queryset.filter(variant__stock=0)


# ===== GRAPHQL INPUT TYPES =====

class CartFilterInput(InputObjectType):
    """Input filter cho Cart"""
    user = graphene.ID(description="Lọc theo user ID")
    session_key = graphene.String(description="Lọc theo session key")
    created_after = graphene.DateTime(description="Tạo sau thời điểm")
    created_before = graphene.DateTime(description="Tạo trước thời điểm")
    is_expired = graphene.Boolean(description="Đã hết hạn")
    has_items = graphene.Boolean(description="Có items")
    total_amount_min = graphene.Decimal(description="Tổng giá trị tối thiểu")
    total_amount_max = graphene.Decimal(description="Tổng giá trị tối đa")


class CartItemFilterInput(InputObjectType):
    """Input filter cho CartItem"""
    cart = graphene.ID(description="Lọc theo cart ID")
    cart_user = graphene.ID(description="Lọc theo user ID của cart")
    variant = graphene.ID(description="Lọc theo variant ID")
    product = graphene.ID(description="Lọc theo product ID")
    category = graphene.ID(description="Lọc theo category ID")
    unit_price_min = graphene.Decimal(description="Giá tối thiểu")
    unit_price_max = graphene.Decimal(description="Giá tối đa")
    quantity_min = graphene.Int(description="Số lượng tối thiểu")
    quantity_max = graphene.Int(description="Số lượng tối đa")
    price_changed = graphene.Boolean(description="Giá có thay đổi")
    is_available = graphene.Boolean(description="Còn có sẵn")


class WishlistFilterInput(InputObjectType):
    """Input filter cho Wishlist"""
    user = graphene.ID(description="Lọc theo user ID")
    variant = graphene.ID(description="Lọc theo variant ID")
    product = graphene.ID(description="Lọc theo product ID")
    category = graphene.ID(description="Lọc theo category ID")
    created_after = graphene.DateTime(description="Tạo sau thời điểm")
    created_before = graphene.DateTime(description="Tạo trước thời điểm")
    is_available = graphene.Boolean(description="Còn có sẵn")
    is_in_stock = graphene.Boolean(description="Còn hàng")


# ===== SORT INPUT TYPES =====

class CartSortInput(InputObjectType):
    """Input sort cho Cart"""
    field = graphene.String(required=True, description="Trường để sort")
    direction = graphene.String(default_value="ASC", description="Hướng sort: ASC/DESC")


class CartItemSortInput(InputObjectType):
    """Input sort cho CartItem"""
    field = graphene.String(required=True, description="Trường để sort")
    direction = graphene.String(default_value="ASC", description="Hướng sort: ASC/DESC")


class WishlistSortInput(InputObjectType):
    """Input sort cho Wishlist"""
    field = graphene.String(required=True, description="Trường để sort")
    direction = graphene.String(default_value="ASC", description="Hướng sort: ASC/DESC")


# ===== HELPER FUNCTIONS =====

def apply_cart_filters(queryset, filters):
    """Áp dụng filters cho Cart queryset"""
    if not filters:
        return queryset
    
    filterset = CartFilterSet(filters, queryset=queryset)
    return filterset.qs


def apply_cart_item_filters(queryset, filters):
    """Áp dụng filters cho CartItem queryset"""
    if not filters:
        return queryset
    
    filterset = CartItemFilterSet(filters, queryset=queryset)
    return filterset.qs


def apply_wishlist_filters(queryset, filters):
    """Áp dụng filters cho Wishlist queryset"""
    if not filters:
        return queryset
    
    filterset = WishlistFilterSet(filters, queryset=queryset)
    return filterset.qs


def apply_cart_sort(queryset, sort_by):
    """Áp dụng sorting cho Cart"""
    if not sort_by:
        return queryset.order_by('-updated_at')
    
    field = sort_by.get('field', 'updated_at')
    direction = sort_by.get('direction', 'ASC')
    
    if direction.upper() == 'DESC':
        field = f'-{field}'
    
    return queryset.order_by(field)


def apply_cart_item_sort(queryset, sort_by):
    """Áp dụng sorting cho CartItem"""
    if not sort_by:
        return queryset.order_by('-updated_at')
    
    field = sort_by.get('field', 'updated_at')
    direction = sort_by.get('direction', 'ASC')
    
    if direction.upper() == 'DESC':
        field = f'-{field}'
    
    return queryset.order_by(field)


def apply_wishlist_sort(queryset, sort_by):
    """Áp dụng sorting cho Wishlist"""
    if not sort_by:
        return queryset.order_by('-created_at')
    
    field = sort_by.get('field', 'created_at')
    direction = sort_by.get('direction', 'ASC')
    
    if direction.upper() == 'DESC':
        field = f'-{field}'
    
    return queryset.order_by(field)