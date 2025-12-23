from django.db import models
from django.conf import settings
from django.utils import timezone


class ReturnRequest(models.Model):
    """
    Yêu cầu trả hàng/hoàn tiền
    Flow: Buyer tạo request → Shop duyệt → Buyer gửi hàng về → Shop kiểm tra → Hoàn tiền
    """
    
    STATUS_CHOICES = [
        ('pending', 'Chờ duyệt'),
        ('approved', 'Đã duyệt - Chờ gửi hàng'),
        ('rejected', 'Từ chối'),
        ('shipping_back', 'Đang gửi hàng về'),
        ('received', 'Shop đã nhận hàng'),
        ('completed', 'Hoàn thành'),
        ('cancelled', 'Đã hủy'),
    ]
    
    REASON_CHOICES = [
        ('wrong_item', 'Giao sai sản phẩm'),
        ('damaged', 'Hàng bị hỏng/lỗi'),
        ('not_as_described', 'Không đúng mô tả'),
        ('size_issue', 'Không vừa size'),
        ('changed_mind', 'Đổi ý không muốn mua'),
        ('quality_issue', 'Chất lượng kém'),
        ('other', 'Lý do khác'),
    ]
    
    TYPE_CHOICES = [
        ('refund', 'Trả hàng hoàn tiền'),
        ('exchange', 'Đổi hàng'),
    ]
    
    return_id = models.AutoField(primary_key=True, verbose_name="Mã yêu cầu")
    
    # Liên kết
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='return_requests',
        verbose_name="Đơn hàng"
    )
    sub_order = models.ForeignKey(
        'orders.SubOrder',
        on_delete=models.CASCADE,
        related_name='return_requests',
        verbose_name="Đơn hàng con",
        null=True,
        blank=True
    )
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='return_requests',
        verbose_name="Người mua"
    )    
    # Exchange order - Order mới được tạo khi đổi hàng
    exchange_order = models.ForeignKey(
        'orders.Order',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='exchange_from_returns',
        verbose_name="Đơn hàng đổi",
        help_text="Order mới được tạo khi type=exchange"
    )    
    # Thông tin yêu cầu
    return_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='refund',
        verbose_name="Loại yêu cầu"
    )
    reason = models.CharField(
        max_length=50,
        choices=REASON_CHOICES,
        verbose_name="Lý do"
    )
    description = models.TextField(verbose_name="Mô tả chi tiết")
    
    # Số tiền hoàn
    refund_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Số tiền hoàn",
        null=True,
        blank=True
    )
    
    # Trạng thái
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Trạng thái"
    )
    
    # Vận chuyển trả hàng
    return_tracking_code = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Mã vận đơn trả hàng"
    )
    
    # Phản hồi từ shop
    shop_response = models.TextField(
        null=True,
        blank=True,
        verbose_name="Phản hồi của shop"
    )
    reject_reason = models.TextField(
        null=True,
        blank=True,
        verbose_name="Lý do từ chối"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật")
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name="Ngày duyệt")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Ngày hoàn thành")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Yêu cầu trả hàng"
        verbose_name_plural = "Yêu cầu trả hàng"
    
    def __str__(self):
        return f"Return #{self.return_id} - Order #{self.order.order_id}"
    
    def can_create_return(self):
        """
        Kiểm tra điều kiện tạo yêu cầu trả hàng:
        - Order đã completed
        - Trong vòng 7 ngày
        - Chưa có return request đang xử lý
        """
        if self.order.status != 'completed':
            return False, "Đơn hàng chưa hoàn thành"
        
        # Check 7 days return policy
        if self.sub_order and self.sub_order.delivered_at:
            days_since_delivery = (timezone.now() - self.sub_order.delivered_at).days
            if days_since_delivery > 7:
                return False, "Đã quá thời gian trả hàng (7 ngày)"
        
        # Check existing pending/approved requests
        existing = ReturnRequest.objects.filter(
            order=self.order,
            status__in=['pending', 'approved', 'shipping_back', 'received']
        ).exists()
        
        if existing:
            return False, "Đơn hàng đã có yêu cầu trả hàng đang xử lý"
        
        return True, "OK"


class ReturnItem(models.Model):
    """Chi tiết sản phẩm trong yêu cầu trả hàng"""
    
    return_request = models.ForeignKey(
        ReturnRequest,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Yêu cầu trả hàng"
    )
    order_item = models.ForeignKey(
        'orders.OrderItem',
        on_delete=models.CASCADE,
        related_name='return_items',
        verbose_name="Sản phẩm đơn hàng"
    )
    quantity = models.IntegerField(verbose_name="Số lượng trả")
    
    class Meta:
        verbose_name = "Sản phẩm trả hàng"
        verbose_name_plural = "Sản phẩm trả hàng"
    
    def __str__(self):
        return f"{self.order_item.variant.product.name} x{self.quantity}"


class ReturnImage(models.Model):
    """Ảnh chứng minh cho yêu cầu trả hàng"""
    
    return_request = models.ForeignKey(
        ReturnRequest,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name="Yêu cầu trả hàng"
    )
    image = models.ImageField(
        upload_to='returns/%Y/%m/',
        verbose_name="Ảnh"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Ảnh trả hàng"
        verbose_name_plural = "Ảnh trả hàng"
    
    def __str__(self):
        return f"Image for Return #{self.return_request.return_id}"


class ReturnTracking(models.Model):
    """Lịch sử xử lý yêu cầu trả hàng"""
    
    return_request = models.ForeignKey(
        ReturnRequest,
        on_delete=models.CASCADE,
        related_name='tracking_history',
        verbose_name="Yêu cầu trả hàng"
    )
    status = models.CharField(max_length=20, verbose_name="Trạng thái")
    note = models.TextField(verbose_name="Ghi chú")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Người thực hiện"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Lịch sử trả hàng"
        verbose_name_plural = "Lịch sử trả hàng"
    
    def __str__(self):
        return f"{self.status} - {self.created_at}"
