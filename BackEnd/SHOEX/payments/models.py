from django.db import models
from django.contrib.auth import get_user_model
from store.models import Store 
from django.utils import timezone
User = get_user_model()


class Payment(models.Model):
    """Thanh toán"""
    
    PAYMENT_METHOD_CHOICES = [
        ('cod', 'Thanh toán khi nhận hàng (COD)'),
        ('vnpay', 'Thanh toán qua VNPAY'),
        ('qr', 'Thanh toán QR / Chuyển khoản'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Chờ thanh toán'),
        ('completed', 'Hoàn thành'),
        ('failed', 'Thất bại'),
        ('cancelled', 'Đã hủy'),
        ('refunded', 'Đã hoàn tiền'),
    ]
    
    payment_id = models.AutoField(
        primary_key=True,
        verbose_name="Mã thanh toán"
    )
    
    order = models.OneToOneField(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='payment',
        verbose_name="Đơn hàng"
    )
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, null=True, blank=True, related_name='payments')
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name="Đến cửa hàng",
        null=True,   # tạm cho phép null để tạo migration an toàn
        blank=True
    )    
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        verbose_name="Phương thức thanh toán"
    )
    
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Số tiền"
    )
    
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Trạng thái"
    )
    
    transaction_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Mã giao dịch"
    )
    
    gateway_response = models.JSONField(
        blank=True,
        null=True,
        verbose_name="Phản hồi từ gateway"
    )
    
    paid_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Thời gian thanh toán"
    )
    
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Ngày cập nhật"
    )
    
    class Meta:
        verbose_name = "Thanh toán"
        verbose_name_plural = "Thanh toán"
    
    def __str__(self):
        return f"Payment {self.payment_id} - {self.get_payment_method_display()}"

