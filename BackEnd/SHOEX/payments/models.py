from django.db import models

class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('paypal', 'PayPal'),
        ('vnpay', 'VNPay'),
        ('cod', 'Cash on Delivery'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    payment_id = models.AutoField(
        primary_key=True,
        verbose_name="Mã thanh toán"
    )
    
    # Map với order_id UNIQUE trong datanew
    order = models.OneToOneField(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='payment',
        verbose_name="Đơn hàng"
    )
    
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Số tiền"
    )
    
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        verbose_name="Phương thức thanh toán"
    )
    
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Trạng thái giao dịch"
    )
    
    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Mã giao dịch (từ cổng TT)"
    )
    
    paid_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Thời gian thanh toán"
    )

    def __str__(self):
        return f"Payment #{self.payment_id} - {self.status}"