from django.db import models

class Payment(models.Model):
    
    PAYMENT_METHOD_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('cod', 'Cash on Delivery'),
    ] 
    
    PAYMENT_METHOD_CHOICES = [
        ('paypal', 'PayPal'),
        ('vnpay', 'VNPay'),
        ('cod', 'Cash on Delivery'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    payment_id = models.AutoField(
        primary_key=True,
        verbose_name="Mã thanh toán",
        help_text="Mã định danh duy nhất cho thanh toán."
    )
    order = models.OneToOneField(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='payment',
        verbose_name="Đơn hàng",
        help_text="Đơn hàng liên kết với thanh toán này."
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Số tiền",
        help_text="Tổng số tiền của thanh toán."
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        verbose_name="Phương thức thanh toán",
        help_text="Phương thức được sử dụng cho thanh toán."
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Trạng thái",
        help_text="Trạng thái hiện tại của thanh toán."
    )
    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Mã giao dịch",
        help_text="Mã giao dịch được cung cấp bởi cổng thanh toán."
    )
    paid_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Thời gian thanh toán",
        help_text="Ngày và giờ khi thanh toán được hoàn thành."
    )

    def __str__(self):
        return f"Thanh toán {self.payment_id}"
