from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from decimal import Decimal

User = get_user_model()

class Cart(models.Model):
    """
    Giỏ hàng - Quản lý thông tin giỏ hàng của user
    Hỗ trợ cả user đã đăng nhập và guest user (session-based)
    """
    cart_id = models.AutoField(
        primary_key=True,
        verbose_name="Mã giỏ hàng"
    )
    
    # User - có thể null cho guest user
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='cart',
        verbose_name="Người dùng"
    )
    
    # Session ID cho guest user
    session_key = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        verbose_name="Session ID",
        help_text="Session ID cho guest user"
    )
    
    # Metadata
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Ngày tạo"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Ngày cập nhật"
    )
    
    # Thời gian hết hạn cho guest cart
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Ngày hết hạn",
        help_text="Thời gian hết hạn cho giỏ hàng guest"
    )
    
    class Meta:
        verbose_name = "Giỏ hàng"
        verbose_name_plural = "Giỏ hàng"
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['session_key']),
            models.Index(fields=['expires_at']),
        ]
        constraints = [
            # Đảm bảo mỗi cart phải có user HOẶC session_key
            models.CheckConstraint(
                check=models.Q(user__isnull=False) | models.Q(session_key__isnull=False),
                name='cart_must_have_user_or_session'
            ),
        ]
    
    def __str__(self):
        if self.user:
            return f"Giỏ hàng của {self.user.username}"
        return f"Giỏ hàng guest - {self.session_key}"
    
    @property
    def total_items(self):
        """Tổng số sản phẩm khác nhau trong giỏ hàng"""
        return self.items.count()
    
    @property
    def total_amount(self):
        """Tổng giá trị giỏ hàng"""
        total = Decimal('0.00')
        for item in self.items.select_related('variant__product'):
            total += item.subtotal
        return total
    
    @property
    def total_weight(self):
        """Tổng khối lượng giỏ hàng (để tính phí ship)"""
        total = Decimal('0.00')
        for item in self.items.select_related('variant'):
            total += item.variant.weight * item.quantity
        return total
    
    def clear(self):
        """Xóa tất cả sản phẩm trong giỏ hàng"""
        self.items.all().delete()
    
    def merge_cart(self, other_cart):
        """Gộp giỏ hàng khác vào giỏ hàng này (khi user login)"""
        for other_item in other_cart.items.all():
            try:
                # Kiểm tra xem sản phẩm đã có trong giỏ hàng chưa
                existing_item = self.items.get(variant=other_item.variant)
                existing_item.quantity += other_item.quantity
                existing_item.save()
            except CartItem.DoesNotExist:
                # Tạo mới nếu chưa có
                CartItem.objects.create(
                    cart=self,
                    variant=other_item.variant,
                    quantity=other_item.quantity
                )
        
        # Xóa giỏ hàng cũ
        other_cart.delete()


class CartItem(models.Model):
    """
    Item trong giỏ hàng - Quản lý từng sản phẩm trong giỏ hàng
    """
    item_id = models.AutoField(
        primary_key=True,
        verbose_name="Mã item"
    )
    
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Giỏ hàng"
    )
    
    variant = models.ForeignKey(
        'products.ProductVariant',
        on_delete=models.CASCADE,
        related_name='cart_items',
        verbose_name="Biến thể sản phẩm"
    )
    
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name="Số lượng"
    )
    
    # Lưu giá tại thời điểm thêm vào giỏ (để tránh thay đổi giá ảnh hưởng)
    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Đơn giá",
        help_text="Giá tại thời điểm thêm vào giỏ hàng"
    )
    
    # Metadata
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Ngày thêm vào giỏ"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Ngày cập nhật"
    )
    
    class Meta:
        verbose_name = "Sản phẩm trong giỏ hàng"
        verbose_name_plural = "Sản phẩm trong giỏ hàng"
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['cart']),
            models.Index(fields=['variant']),
        ]
        constraints = [
            # Đảm bảo không có sản phẩm trùng lặp trong cùng một giỏ hàng
            models.UniqueConstraint(
                fields=['cart', 'variant'],
                name='unique_cart_variant'
            ),
        ]
    
    def __str__(self):
        return f"{self.variant.product.name} ({self.variant.sku}) x{self.quantity}"
    
    @property
    def subtotal(self):
        """Tính tổng tiền cho item này"""
        return self.unit_price * self.quantity
    
    @property
    def current_price(self):
        """Giá hiện tại của sản phẩm (để so sánh với unit_price)"""
        return self.variant.price
    
    @property
    def price_changed(self):
        """Kiểm tra xem giá có thay đổi so với lúc thêm vào giỏ không"""
        return self.unit_price != self.current_price
    
    def save(self, *args, **kwargs):
        # Tự động set unit_price từ variant nếu chưa có
        if not self.unit_price:
            self.unit_price = self.variant.price
        
        # Kiểm tra tồn kho
        if self.quantity > self.variant.stock:
            raise ValidationError(
                f"Số lượng yêu cầu ({self.quantity}) vượt quá tồn kho ({self.variant.stock})"
            )
        
        super().save(*args, **kwargs)
    
    def clean(self):
        """Validate dữ liệu"""
        if self.quantity <= 0:
            raise ValidationError("Số lượng phải lớn hơn 0")
        
        if not self.variant.is_active:
            raise ValidationError("Không thể thêm sản phẩm ngừng bán vào giỏ hàng")
        
        if not self.variant.product.is_active:
            raise ValidationError("Không thể thêm sản phẩm ngừng bán vào giỏ hàng")


class Wishlist(models.Model):
    """
    Danh sách yêu thích - Sản phẩm user quan tâm nhưng chưa mua
    """
    wishlist_id = models.AutoField(
        primary_key=True,
        verbose_name="Mã wishlist"
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='wishlists',
        verbose_name="Người dùng"
    )
    
    variant = models.ForeignKey(
        'products.ProductVariant',
        on_delete=models.CASCADE,
        related_name='wishlisted_by',
        verbose_name="Biến thể sản phẩm"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Ngày thêm vào wishlist"
    )
    
    class Meta:
        verbose_name = "Danh sách yêu thích"
        verbose_name_plural = "Danh sách yêu thích"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['variant']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'variant'],
                name='unique_user_wishlist_variant'
            ),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.variant.product.name}"
    
    def move_to_cart(self, quantity=1):
        """Chuyển sản phẩm từ wishlist vào giỏ hàng"""
        cart, created = Cart.objects.get_or_create(user=self.user)
        try:
            cart_item = CartItem.objects.get(cart=cart, variant=self.variant)
            cart_item.quantity += quantity
            cart_item.save()
        except CartItem.DoesNotExist:
            CartItem.objects.create(
                cart=cart,
                variant=self.variant,
                quantity=quantity
            )
        self.delete()
