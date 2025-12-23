from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

class Voucher(models.Model):
    """
    Quản lý thông tin voucher
    """
    TYPE_CHOICES = [
        ('platform', 'Platform'),
        ('store', 'Store'), # Đổi từ 'seller' sang 'store' cho đúng ngữ cảnh mới
        ('shipping', 'Shipping'),
    ]
    
    DISCOUNT_TYPE_CHOICES = [
        ('percent', 'Percent'),
        ('fixed', 'Fixed'),
    ]

    voucher_id = models.AutoField(
        primary_key=True,
        verbose_name="Mã voucher"
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Mã voucher"
    )
    type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        verbose_name="Loại voucher"
    )
    
    # --- THAY ĐỔI QUAN TRỌNG: Link tới Store thay vì User ---
    # Cột trong DB tên là seller_id (varchar 50), trỏ tới store_store
    seller = models.ForeignKey(
        'store.Store', 
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='vouchers',
        verbose_name="Cửa hàng sở hữu",
        db_column='seller_id' # Map đúng với tên cột trong SQL
    )
    # -------------------------------------------------------

    discount_type = models.CharField(
        max_length=10,
        choices=DISCOUNT_TYPE_CHOICES,
        verbose_name="Loại giảm giá"
    )
    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Giá trị giảm"
    )
    min_order_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Đơn tối thiểu"
    )
    max_discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Giảm tối đa"
    )
    start_date = models.DateField(verbose_name="Ngày bắt đầu")
    end_date = models.DateField(verbose_name="Ngày hết hạn")
    usage_limit = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        verbose_name="Giới hạn sử dụng toàn hệ thống"
    )
    per_user_limit = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name="Giới hạn mỗi user"
    )
    is_active = models.BooleanField(default=True, verbose_name="Kích hoạt")
    is_auto = models.BooleanField(default=False, verbose_name="Tự động áp")
    is_free_shipping = models.BooleanField(default=False, verbose_name="Miễn phí vận chuyển")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Voucher"
        verbose_name_plural = "Vouchers"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.code} - {self.get_type_display()}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.type == 'store' and not self.seller:
            raise ValidationError("Store voucher phải thuộc về một cửa hàng cụ thể.")
        if self.type == 'platform' and self.seller:
            raise ValidationError("Platform voucher không được gán cho cửa hàng.")
        if self.type == 'shipping' and self.seller:
            raise ValidationError("Shipping voucher không được gán cho cửa hàng.")
        if self.end_date <= self.start_date:
            raise ValidationError("Ngày kết thúc phải sau ngày bắt đầu.")


class VoucherProduct(models.Model):
    """Liên kết voucher với sản phẩm"""
    voucher = models.ForeignKey(
        Voucher,
        on_delete=models.CASCADE,
        related_name='voucher_products'
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='voucher_products'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['voucher', 'product']


class VoucherCategory(models.Model):
    """Liên kết voucher với danh mục"""
    voucher = models.ForeignKey(
        Voucher,
        on_delete=models.CASCADE,
        related_name='voucher_categories'
    )
    category = models.ForeignKey(
        'products.Category',
        on_delete=models.CASCADE,
        related_name='voucher_categories'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['voucher', 'category']


# --- MODEL MỚI: Khớp với bảng discount_voucherstore trong DB ---
class VoucherStore(models.Model):
    """
    Liên kết voucher (Platform) áp dụng cho các Store cụ thể
    """
    voucher = models.ForeignKey(
        Voucher,
        on_delete=models.CASCADE,
        related_name='voucher_stores'
    )
    store = models.ForeignKey(
        'store.Store',
        on_delete=models.CASCADE,
        related_name='applied_platform_vouchers'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['voucher', 'store']
        verbose_name = "Voucher - Cửa hàng áp dụng"


class VoucherSeller(models.Model):
    """
    Giữ lại model này vì bảng discount_voucherseller VẪN TỒN TẠI trong datanew.sql
    Tuy nhiên, logic nghiệp vụ nên ưu tiên dùng VoucherStore.
    Bảng này liên kết Voucher với User (Seller cũ).
    """
    voucher = models.ForeignKey(Voucher, on_delete=models.CASCADE)
    seller = models.ForeignKey('users.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['voucher', 'seller']


class UserVoucher(models.Model):
    """Quản lý ví voucher của người dùng"""
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='user_vouchers'
    )
    voucher = models.ForeignKey(
        Voucher,
        on_delete=models.CASCADE,
        related_name='user_vouchers'
    )
    saved_at = models.DateTimeField(auto_now_add=True)
    used_count = models.IntegerField(default=0)

    class Meta:
        unique_together = ['user', 'voucher']
        ordering = ['-saved_at']

    @property
    def can_use(self):
        return self.used_count < self.voucher.per_user_limit


class OrderVoucher(models.Model):
    """Lịch sử áp dụng voucher vào đơn hàng"""
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='order_vouchers'
    )
    voucher = models.ForeignKey(
        Voucher,
        on_delete=models.CASCADE,
        related_name='order_vouchers'
    )
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    applied_at = models.DateTimeField(auto_now_add=True)


class VoucherReservation(models.Model):
    """Đặt giữ voucher tạm thời cho user trong quá trình checkout

    Nếu user không hoàn tất đặt hàng trong thời gian `expires_at`, reservation nên được
    dọn dẹp (cron/job) hoặc user có thể gọi `release` để trả lại voucher.
    """
    reservation_id = models.AutoField(primary_key=True)
    voucher = models.ForeignKey(Voucher, on_delete=models.CASCADE, related_name='reservations')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='voucher_reservations')
    reserved_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        verbose_name = "Voucher Reservation"
        verbose_name_plural = "Voucher Reservations"


class VoucherUsage(models.Model):
    """Ghi nhận số lần một user đã sử dụng một voucher.

    Dùng để giới hạn `per_user_limit` một cách chắc chắn (không phụ thuộc vào việc
    người dùng có lưu voucher trong ví hay không).
    """
    id = models.AutoField(primary_key=True)
    voucher = models.ForeignKey(Voucher, on_delete=models.CASCADE, related_name='usages')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='voucher_usages')
    used_count = models.IntegerField(default=0)
    last_used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['voucher', 'user']
        verbose_name = 'Voucher Usage'
        verbose_name_plural = 'Voucher Usages'