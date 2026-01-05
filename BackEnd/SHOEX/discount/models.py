from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from django.core.exceptions import ValidationError # Thêm import này


class Voucher(models.Model):
    TYPE_CHOICES = [
        ('platform', 'Platform'),
        ('store', 'Store'),
    ]
    
    DISCOUNT_TYPE_CHOICES = [
        ('percent', 'Percent'),
        ('fixed', 'Fixed'),
        ('freeship', 'Free Shipping'),
    ]

    voucher_id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=50, unique=False, null=True, blank=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=200, unique=False, null=True, blank=True)
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    start_date = models.DateField()
    end_date = models.DateField()

    usage_limit = models.IntegerField(null=True, blank=True)
    per_user_limit = models.IntegerField(default=1)

    is_active = models.BooleanField(default=True)
    is_auto = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def clean(self):
        if self.end_date <= self.start_date:
            raise ValidationError("Ngày kết thúc phải sau ngày bắt đầu")

        else:
            if self.discount_type == 'fixed' and self.max_discount:
                raise ValidationError("Max discount chỉ áp dụng cho voucher phần trăm")




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


# Đã loại bỏ Mô hình VoucherSeller


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


class VoucherStore(models.Model):
    """
    Liên kết voucher platform với nhiều cửa hàng (tùy chọn)
    Dùng khi voucher platform áp dụng cho một số cửa hàng cụ thể
    """
    
    voucher = models.ForeignKey(
        Voucher,
        on_delete=models.CASCADE,
        related_name='voucher_stores',
        verbose_name="Voucher"
    )
    
    store = models.ForeignKey(
        'store.Store',
        on_delete=models.CASCADE,
        related_name='applicable_vouchers',
        verbose_name="Cửa hàng"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Ngày tạo"
    )
    
    class Meta:
        verbose_name = "Voucher cho cửa hàng"
        verbose_name_plural = "Voucher cho cửa hàng"
        constraints = [
            models.UniqueConstraint(
                fields=['voucher', 'store'],
                name='unique_voucher_store'
            ),
        ]
    
    def __str__(self):
        return f"{self.voucher.code} - {self.store.name}"