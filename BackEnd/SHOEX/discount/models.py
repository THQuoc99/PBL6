from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class Voucher(models.Model):
    """
    Quản lý thông tin voucher chung
    """
    TYPE_CHOICES = [
        ('platform', 'Platform'),
        ('seller', 'Seller'),
    ]
    
    DISCOUNT_TYPE_CHOICES = [
        ('percent', 'Percent'),
        ('fixed', 'Fixed'),
    ]

    voucher_id = models.AutoField(
        primary_key=True,
        verbose_name="Mã voucher",
        help_text="ID tự tăng, duy nhất cho mỗi voucher"
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Mã voucher",
        help_text="Mã voucher duy nhất để người dùng nhập"
    )
    type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        verbose_name="Loại voucher",
        help_text="Platform voucher hoặc seller voucher"
    )
    seller = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='vouchers',
        verbose_name="Người bán",
        help_text="Người bán sở hữu voucher (NULL nếu là platform voucher)"
    )
    discount_type = models.CharField(
        max_length=10,
        choices=DISCOUNT_TYPE_CHOICES,
        verbose_name="Loại giảm giá",
        help_text="Giảm theo phần trăm hoặc số tiền cố định"
    )
    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Giá trị giảm",
        help_text="Giá trị giảm giá (% hoặc số tiền)"
    )
    min_order_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Đơn tối thiểu",
        help_text="Số tiền đơn hàng tối thiểu để áp dụng voucher"
    )
    max_discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Giảm tối đa",
        help_text="Số tiền giảm tối đa (dành cho voucher %)"
    )
    start_date = models.DateField(
        verbose_name="Ngày bắt đầu",
        help_text="Ngày bắt đầu có hiệu lực"
    )
    end_date = models.DateField(
        verbose_name="Ngày hết hạn",
        help_text="Ngày hết hạn voucher"
    )
    usage_limit = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        verbose_name="Giới hạn sử dụng",
        help_text="Số lượt sử dụng tối đa toàn hệ thống (NULL = không giới hạn)"
    )
    per_user_limit = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name="Giới hạn mỗi user",
        help_text="Số lượt sử dụng tối đa mỗi user"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Trạng thái",
        help_text="Voucher có đang hoạt động không"
    )
    is_auto = models.BooleanField(
        default=False,
        verbose_name="Tự động áp dụng",
        help_text="True = tự động áp dụng, False = phải nhập mã"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Ngày tạo",
        help_text="Ngày giờ voucher được tạo"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Ngày cập nhật",
        help_text="Ngày giờ voucher được cập nhật lần cuối"
    )

    class Meta:
        verbose_name = "Voucher"
        verbose_name_plural = "Vouchers"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.code} - {self.get_type_display()}"

    def clean(self):
        from django.core.exceptions import ValidationError
        
        # Validation: Seller voucher phải có seller_id
        if self.type == 'seller' and not self.seller:
            raise ValidationError("Seller voucher phải có thông tin seller")
        
        # Validation: Platform voucher không được có seller_id
        if self.type == 'platform' and self.seller:
            raise ValidationError("Platform voucher không được có thông tin seller")
        
        # Validation: Ngày kết thúc phải sau ngày bắt đầu
        if self.end_date <= self.start_date:
            raise ValidationError("Ngày kết thúc phải sau ngày bắt đầu")
        
        # Validation: max_discount chỉ áp dụng cho discount_type = percent
        if self.discount_type == 'fixed' and self.max_discount:
            raise ValidationError("Max discount chỉ áp dụng cho voucher giảm theo %")


class VoucherProduct(models.Model):
    """
    Liên kết voucher với sản phẩm cụ thể
    """
    voucher = models.ForeignKey(
        Voucher,
        on_delete=models.CASCADE,
        related_name='voucher_products',
        verbose_name="Voucher"
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='voucher_products',
        verbose_name="Sản phẩm"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Ngày tạo"
    )

    class Meta:
        unique_together = ['voucher', 'product']
        verbose_name = "Voucher - Sản phẩm"
        verbose_name_plural = "Voucher - Sản phẩm"

    def __str__(self):
        return f"{self.voucher.code} - {self.product.name}"


class VoucherCategory(models.Model):
    """
    Liên kết voucher với danh mục sản phẩm
    """
    voucher = models.ForeignKey(
        Voucher,
        on_delete=models.CASCADE,
        related_name='voucher_categories',
        verbose_name="Voucher"
    )
    category = models.ForeignKey(
        'products.Category',
        on_delete=models.CASCADE,
        related_name='voucher_categories',
        verbose_name="Danh mục"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Ngày tạo"
    )

    class Meta:
        unique_together = ['voucher', 'category']
        verbose_name = "Voucher - Danh mục"
        verbose_name_plural = "Voucher - Danh mục"

    def __str__(self):
        return f"{self.voucher.code} - {self.category.name}"


class VoucherSeller(models.Model):
    """
    Liên kết voucher với nhiều seller (tùy chọn)
    Dùng khi voucher platform áp dụng cho một số seller cụ thể
    """
    voucher = models.ForeignKey(
        Voucher,
        on_delete=models.CASCADE,
        related_name='voucher_sellers',
        verbose_name="Voucher"
    )
    seller = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='voucher_sellers',
        verbose_name="Người bán"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Ngày tạo"
    )

    class Meta:
        unique_together = ['voucher', 'seller']
        verbose_name = "Voucher - Seller"
        verbose_name_plural = "Voucher - Seller"

    def __str__(self):
        return f"{self.voucher.code} - {self.seller.username}"


class UserVoucher(models.Model):
    """
    Quản lý user đã lưu voucher nào và số lần sử dụng
    """
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='user_vouchers',
        verbose_name="Người dùng"
    )
    voucher = models.ForeignKey(
        Voucher,
        on_delete=models.CASCADE,
        related_name='user_vouchers',
        verbose_name="Voucher"
    )
    saved_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Thời điểm lưu",
        help_text="Thời điểm user lưu voucher"
    )
    used_count = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Số lần đã sử dụng",
        help_text="Số lần user đã sử dụng voucher này"
    )

    class Meta:
        unique_together = ['user', 'voucher']
        verbose_name = "User - Voucher"
        verbose_name_plural = "User - Voucher"
        ordering = ['-saved_at']

    def __str__(self):
        return f"{self.user.username} - {self.voucher.code}"

    @property
    def can_use(self):
        """Kiểm tra user có thể sử dụng voucher này không"""
        return self.used_count < self.voucher.per_user_limit


class OrderVoucher(models.Model):
    """
    Lưu voucher được áp dụng cho đơn hàng
    """
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='order_vouchers',
        verbose_name="Đơn hàng"
    )
    voucher = models.ForeignKey(
        Voucher,
        on_delete=models.CASCADE,
        related_name='order_vouchers',
        verbose_name="Voucher"
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Số tiền được giảm",
        help_text="Số tiền thực tế được giảm trong đơn hàng này"
    )
    applied_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Thời điểm áp dụng",
        help_text="Thời điểm voucher được áp dụng vào đơn hàng"
    )

    class Meta:
        verbose_name = "Order - Voucher"
        verbose_name_plural = "Order - Voucher"
        ordering = ['-applied_at']

    def __str__(self):
        return f"Order {self.order.order_id} - {self.voucher.code} (-{self.discount_amount})"
