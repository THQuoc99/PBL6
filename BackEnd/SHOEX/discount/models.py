from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.conf import settings

class Voucher(models.Model):
    """
    Quản lý thông tin voucher
    """
    SCOPE_CHOICES = [
        ('store', 'Voucher của Shop'),      
        ('platform', 'Voucher của Sàn'),    
        ('shipping', 'Voucher Vận chuyển'), 
    ]
    
    DISCOUNT_TYPE_CHOICES = [
        ('fixed', 'Số tiền cố định'),
        ('percent', 'Phần trăm'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('all', 'Tất cả hình thức'),
        ('COD', 'Thanh toán khi nhận hàng (COD)'),
        ('VNPAY', 'Ví điện tử VNPAY'),
        ('PAYPAL', 'PayPal'),
    ]

    voucher_id = models.AutoField(primary_key=True, verbose_name="Mã ID")
    code = models.CharField(max_length=50, unique=True, verbose_name="Mã code")
    
    # Phạm vi áp dụng
    scope = models.CharField(max_length=20, choices=SCOPE_CHOICES, default='store', verbose_name="Phạm vi")
    
    # Link tới Store (Nếu là Voucher Shop)
    store = models.ForeignKey(
        'store.Store',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='shop_vouchers',
        verbose_name="Cửa hàng sở hữu"
    )
    
    # Để tương thích ngược nếu code cũ dùng 'seller'
    # Bạn có thể dùng @property hoặc giữ field này nếu DB cũ có cột seller_id
    # Ở đây ta ưu tiên dùng 'store'.

    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES, verbose_name="Loại giảm giá")
    discount_value = models.DecimalField(
        max_digits=10, decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))], 
        verbose_name="Giá trị giảm"
    )
    
    # Điều kiện áp dụng
    min_order_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('0.00'),
        verbose_name="Đơn tối thiểu"
    )
    max_discount = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
        verbose_name="Giảm tối đa (cho %)"
    )
    
    start_date = models.DateTimeField(verbose_name="Ngày bắt đầu")
    end_date = models.DateTimeField(verbose_name="Ngày hết hạn")
    
    # Quản lý số lượng
    usage_limit = models.IntegerField(null=True, blank=True, verbose_name="Tổng lượt dùng toàn sàn")
    per_user_limit = models.IntegerField(default=1, verbose_name="Giới hạn mỗi người")
    
    is_active = models.BooleanField(default=True, verbose_name="Kích hoạt")
    is_free_shipping = models.BooleanField(default=False, verbose_name="Là mã Freeship")
    
    # Điều kiện thanh toán
    payment_method_required = models.CharField(
        max_length=20, 
        choices=PAYMENT_METHOD_CHOICES, 
        default='all',
        verbose_name="Yêu cầu phương thức thanh toán"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Voucher"
        verbose_name_plural = "Vouchers"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.code} ({self.get_scope_display()})"

    # Thuộc tính tương thích cho code cũ (nếu có gọi voucher.type)
    @property
    def type(self):
        return self.scope


# --- CÁC MODEL BỔ TRỢ (QUAN TRỌNG ĐỂ KHÔNG BỊ LỖI IMPORT ADMIN) ---

class VoucherProduct(models.Model):
    """Liên kết voucher với sản phẩm cụ thể"""
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
        verbose_name = "Voucher - Sản phẩm áp dụng"


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
        verbose_name = "Voucher - Danh mục áp dụng"


class VoucherStore(models.Model):
    """
    Dùng cho Voucher Sàn (Platform) nhưng chỉ áp dụng cho một số Shop nhất định.
    """
    voucher = models.ForeignKey(Voucher, on_delete=models.CASCADE, related_name='applicable_stores')
    store = models.ForeignKey('store.Store', on_delete=models.CASCADE, related_name='platform_vouchers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['voucher', 'store']
        verbose_name = "Voucher - Cửa hàng áp dụng (Platform)"


class VoucherSeller(models.Model):
    """
    Model cũ liên kết Voucher với User (Seller). 
    Giữ lại để tránh lỗi import nếu admin.py vẫn gọi.
    """
    voucher = models.ForeignKey(Voucher, on_delete=models.CASCADE)
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['voucher', 'seller']


class UserVoucher(models.Model):
    """Ví Voucher của người dùng"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_vouchers')
    voucher = models.ForeignKey(Voucher, on_delete=models.CASCADE, related_name='saved_by_users')
    saved_at = models.DateTimeField(auto_now_add=True)
    used_count = models.IntegerField(default=0)

    class Meta:
        unique_together = ['user', 'voucher']


class VoucherUsage(models.Model):
    """Lịch sử dùng voucher để chặn spam"""
    voucher = models.ForeignKey(Voucher, on_delete=models.CASCADE, related_name='usages')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='voucher_usages')
    used_count = models.IntegerField(default=0)
    last_used_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['voucher', 'user']


class OrderVoucher(models.Model):
    """Lưu vết voucher đã áp dụng vào đơn hàng"""
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='order_vouchers')
    voucher = models.ForeignKey(Voucher, on_delete=models.CASCADE)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2)
    applied_at = models.DateTimeField(auto_now_add=True)


class VoucherReservation(models.Model):
    """Giữ chỗ voucher khi đang thanh toán"""
    reservation_id = models.AutoField(primary_key=True)
    voucher = models.ForeignKey(Voucher, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reserved_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()