from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Cart, CartItem, Wishlist

class CartItemInline(admin.TabularInline):
    """Inline để hiển thị các items trong giỏ hàng"""
    model = CartItem
    extra = 0
    readonly_fields = ('subtotal_display', 'price_status')
    fields = ('variant', 'quantity', 'unit_price', 'subtotal_display', 'price_status', 'created_at')
    
    def subtotal_display(self, obj):
        """Hiển thị tổng tiền của item"""
        if obj.pk:
            return f"{obj.subtotal:,.0f} ₫"
        return "-"
    subtotal_display.short_description = "Thành tiền"
    
    def price_status(self, obj):
        """Hiển thị trạng thái giá (có thay đổi không)"""
        if obj.pk and obj.price_changed:
            return format_html(
                '<span style="color: red;">Giá đã thay đổi: {} ₫</span>',
                f"{obj.current_price:,.0f}"
            )
        return format_html('<span style="color: green;">Giá không đổi</span>')
    price_status.short_description = "Trạng thái giá"

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Admin cho model Cart"""
    list_display = (
        'cart_id', 
        'user_display', 
        'cart_type', 
        'total_items_display', 
        'total_amount_display',
        'total_weight_display',
        'status_display',
        'created_at', 
        'updated_at'
    )
    list_filter = (
        'created_at', 
        'updated_at', 
        'expires_at',
    )
    search_fields = ('user__username', 'user__email', 'session_key')
    readonly_fields = (
        'cart_id', 
        'total_items_display', 
        'total_amount_display', 
        'total_weight_display',
        'created_at', 
        'updated_at'
    )
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('cart_id', 'user', 'session_key')
        }),
        ('Thống kê', {
            'fields': ('total_items_display', 'total_amount_display', 'total_weight_display')
        }),
        ('Thời gian', {
            'fields': ('created_at', 'updated_at', 'expires_at')
        }),
    )
    inlines = [CartItemInline]
    actions = ['clear_expired_carts', 'clear_selected_carts']
    
    def user_display(self, obj):
        """Hiển thị thông tin user"""
        if obj.user:
            return format_html(
                '<a href="{}">{}</a>',
                reverse('admin:users_user_change', args=[obj.user.pk]),
                obj.user.username
            )
        return "Guest User"
    user_display.short_description = "Người dùng"
    user_display.admin_order_field = 'user__username'
    
    def cart_type(self, obj):
        """Hiển thị loại giỏ hàng"""
        if obj.user:
            return format_html('<span style="color: green;">User Cart</span>')
        return format_html('<span style="color: orange;">Guest Cart</span>')
    cart_type.short_description = "Loại giỏ hàng"
    
    def total_items_display(self, obj):
        """Hiển thị tổng số items"""
        return f"{obj.total_items} sản phẩm"
    total_items_display.short_description = "Tổng số lượng"
    
    def total_amount_display(self, obj):
        """Hiển thị tổng giá trị"""
        return f"{obj.total_amount:,.0f} ₫"
    total_amount_display.short_description = "Tổng giá trị"
    
    def total_weight_display(self, obj):
        """Hiển thị tổng khối lượng"""
        return f"{obj.total_weight:.2f} kg"
    total_weight_display.short_description = "Tổng khối lượng"
    
    def status_display(self, obj):
        """Hiển thị trạng thái giỏ hàng"""
        if obj.expires_at and obj.expires_at < timezone.now():
            return format_html('<span style="color: red;">Đã hết hạn</span>')
        elif obj.total_items == 0:
            return format_html('<span style="color: gray;">Trống</span>')
        else:
            return format_html('<span style="color: green;">Hoạt động</span>')
    status_display.short_description = "Trạng thái"
    
    def clear_expired_carts(self, request, queryset):
        """Action để xóa các giỏ hàng đã hết hạn"""
        from django.utils import timezone
        expired_carts = queryset.filter(expires_at__lt=timezone.now())
        count = expired_carts.count()
        expired_carts.delete()
        self.message_user(request, f"Đã xóa {count} giỏ hàng hết hạn.")
    clear_expired_carts.short_description = "Xóa giỏ hàng hết hạn"
    
    def clear_selected_carts(self, request, queryset):
        """Action để xóa tất cả items trong giỏ hàng được chọn"""
        count = 0
        for cart in queryset:
            items_count = cart.items.count()
            cart.clear()
            count += items_count
        self.message_user(request, f"Đã xóa {count} sản phẩm từ {queryset.count()} giỏ hàng.")
    clear_selected_carts.short_description = "Xóa tất cả sản phẩm trong giỏ hàng"

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """Admin cho model CartItem"""
    list_display = (
        'item_id',
        'cart_display',
        'product_display',
        'variant_info',
        'quantity',
        'unit_price_display',
        'subtotal_display',
        'price_status',
        'stock_status',
        'created_at'
    )
    list_filter = (
        'created_at',
        'updated_at',
        'variant__product__category',
        'variant__product__seller'
    )
    search_fields = (
        'cart__user__username',
        'variant__product__name',
        'variant__sku'
    )
    readonly_fields = (
        'item_id',
        'subtotal_display',
        'price_status',
        'stock_status',
        'created_at',
        'updated_at'
    )
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('item_id', 'cart', 'variant', 'quantity')
        }),
        ('Giá cả', {
            'fields': ('unit_price', 'subtotal_display', 'price_status')
        }),
        ('Trạng thái', {
            'fields': ('stock_status', 'created_at', 'updated_at')
        }),
    )
    actions = ['update_prices', 'remove_out_of_stock']
    
    def cart_display(self, obj):
        """Hiển thị thông tin giỏ hàng"""
        cart_url = reverse('admin:cart_cart_change', args=[obj.cart.pk])
        if obj.cart.user:
            return format_html(
                '<a href="{}">Giỏ hàng #{} ({})</a>',
                cart_url,
                obj.cart.cart_id,
                obj.cart.user.username
            )
        return format_html(
            '<a href="{}">Giỏ hàng #{} (Guest)</a>',
            cart_url,
            obj.cart.cart_id
        )
    cart_display.short_description = "Giỏ hàng"
    
    def product_display(self, obj):
        """Hiển thị thông tin sản phẩm"""
        product_url = reverse('admin:products_product_change', args=[obj.variant.product.pk])
        return format_html(
            '<a href="{}">{}</a>',
            product_url,
            obj.variant.product.name
        )
    product_display.short_description = "Sản phẩm"
    
    def variant_info(self, obj):
        """Hiển thị thông tin variant"""
        variant_url = reverse('admin:products_productvariant_change', args=[obj.variant.pk])
        return format_html(
            '<a href="{}">{}</a><br><small>{}</small>',
            variant_url,
            obj.variant.sku,
            obj.variant.option_combinations
        )
    variant_info.short_description = "Biến thể"
    
    def unit_price_display(self, obj):
        """Hiển thị đơn giá"""
        return f"{obj.unit_price:,.0f} ₫"
    unit_price_display.short_description = "Đơn giá"
    unit_price_display.admin_order_field = 'unit_price'
    
    def subtotal_display(self, obj):
        """Hiển thị thành tiền"""
        return f"{obj.subtotal:,.0f} ₫"
    subtotal_display.short_description = "Thành tiền"
    
    def price_status(self, obj):
        """Hiển thị trạng thái giá"""
        if obj.price_changed:
            return format_html(
                '<span style="color: red;">Đã thay đổi<br>Hiện tại: {:,.0f} ₫</span>',
                obj.current_price
            )
        return format_html('<span style="color: green;">Không đổi</span>')
    price_status.short_description = "Trạng thái giá"
    
    def stock_status(self, obj):
        """Hiển thị trạng thái tồn kho"""
        if obj.quantity > obj.variant.stock:
            return format_html(
                '<span style="color: red;">Vượt tồn kho<br>Còn: {} sản phẩm</span>',
                obj.variant.stock
            )
        elif obj.variant.stock == 0:
            return format_html('<span style="color: red;">Hết hàng</span>')
        elif obj.variant.stock < 10:
            return format_html(
                '<span style="color: orange;">Sắp hết<br>Còn: {} sản phẩm</span>',
                obj.variant.stock
            )
        return format_html('<span style="color: green;">Còn hàng</span>')
    stock_status.short_description = "Trạng thái kho"
    
    def update_prices(self, request, queryset):
        """Action để cập nhật giá theo giá hiện tại"""
        count = 0
        for item in queryset:
            if item.price_changed:
                item.unit_price = item.current_price
                item.save()
                count += 1
        self.message_user(request, f"Đã cập nhật giá cho {count} sản phẩm.")
    update_prices.short_description = "Cập nhật giá theo giá hiện tại"
    
    def remove_out_of_stock(self, request, queryset):
        """Action để xóa các sản phẩm hết hàng"""
        out_of_stock = queryset.filter(variant__stock=0)
        count = out_of_stock.count()
        out_of_stock.delete()
        self.message_user(request, f"Đã xóa {count} sản phẩm hết hàng khỏi giỏ hàng.")
    remove_out_of_stock.short_description = "Xóa sản phẩm hết hàng"

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    """Admin cho model Wishlist (Danh sách yêu thích)"""
    list_display = (
        'wishlist_id',
        'user_display',
        'product_display',
        'variant_info',
        'price_display',
        'stock_status',
        'created_at'
    )
    list_filter = (
        'created_at',
        'variant__product__category',
        'variant__product__seller'
    )
    search_fields = (
        'user__username',
        'user__email',
        'variant__product__name',
        'variant__sku'
    )
    readonly_fields = ('wishlist_id', 'created_at')
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('wishlist_id', 'user', 'variant')
        }),
        ('Thời gian', {
            'fields': ('created_at',)
        }),
    )
    actions = ['move_to_cart', 'remove_out_of_stock_items']
    
    def user_display(self, obj):
        """Hiển thị thông tin user"""
        user_url = reverse('admin:users_user_change', args=[obj.user.pk])
        return format_html(
            '<a href="{}">{}</a>',
            user_url,
            obj.user.username
        )
    user_display.short_description = "Người dùng"
    user_display.admin_order_field = 'user__username'
    
    def product_display(self, obj):
        """Hiển thị thông tin sản phẩm"""
        product_url = reverse('admin:products_product_change', args=[obj.variant.product.pk])
        return format_html(
            '<a href="{}">{}</a>',
            product_url,
            obj.variant.product.name
        )
    product_display.short_description = "Sản phẩm"
    
    def variant_info(self, obj):
        """Hiển thị thông tin variant"""
        variant_url = reverse('admin:products_productvariant_change', args=[obj.variant.pk])
        return format_html(
            '<a href="{}">{}</a><br><small>{}</small>',
            variant_url,
            obj.variant.sku,
            obj.variant.option_combinations
        )
    variant_info.short_description = "Biến thể"
    
    def price_display(self, obj):
        """Hiển thị giá hiện tại"""
        return f"{obj.variant.price:,.0f} ₫"
    price_display.short_description = "Giá hiện tại"
    price_display.admin_order_field = 'variant__price'
    
    def stock_status(self, obj):
        """Hiển thị trạng thái tồn kho"""
        if obj.variant.stock == 0:
            return format_html('<span style="color: red;">Hết hàng</span>')
        elif obj.variant.stock < 10:
            return format_html(
                '<span style="color: orange;">Sắp hết<br>Còn: {} sản phẩm</span>',
                obj.variant.stock
            )
        return format_html('<span style="color: green;">Còn hàng</span>')
    stock_status.short_description = "Trạng thái kho"
    
    def move_to_cart(self, request, queryset):
        """Action để chuyển sản phẩm vào giỏ hàng"""
        count = 0
        for saved_item in queryset:
            try:
                saved_item.move_to_cart()
                count += 1
            except Exception as e:
                self.message_user(
                    request, 
                    f"Lỗi khi chuyển {saved_item.variant.product.name}: {str(e)}",
                    level='ERROR'
                )
        self.message_user(request, f"Đã chuyển {count} sản phẩm vào giỏ hàng.")
    move_to_cart.short_description = "Chuyển vào giỏ hàng"
    
    def remove_out_of_stock_items(self, request, queryset):
        """Action để xóa các sản phẩm hết hàng"""
        out_of_stock = queryset.filter(variant__stock=0)
        count = out_of_stock.count()
        out_of_stock.delete()
        self.message_user(request, f"Đã xóa {count} sản phẩm hét hàng khỏi danh sách yêu thích.")
    remove_out_of_stock_items.short_description = "Xóa sản phẩm hết hàng"

# Import timezone cho các function cần dùng
from django.utils import timezone
