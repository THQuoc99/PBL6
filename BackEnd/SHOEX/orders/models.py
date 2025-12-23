from django.db import models
from django.conf import settings

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Chờ xác nhận'),
        ('processing', 'Đang xử lý'),
        ('shipped', 'Đang giao hàng'),
        ('completed', 'Hoàn thành'),
        ('cancelled', 'Đã hủy'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Chờ thanh toán'),
        ('paid', 'Đã thanh toán'),
        ('failed', 'Thất bại'),
        ('refunded', 'Đã hoàn tiền'),
    ]

    order_id = models.AutoField(primary_key=True, verbose_name="Mã đơn hàng")
    
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name="Người mua"
    )
    
    address = models.ForeignKey(
        'address.Address', 
        on_delete=models.PROTECT,
        related_name='orders',
        verbose_name="Địa chỉ giao hàng"
    )
    
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Tổng tiền")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Trạng thái đơn")
    
    payment_method = models.CharField(max_length=50, default='COD', verbose_name="Phương thức thanh toán")
    
    # --- CÁC TRƯỜNG MỚI TRONG DATANEW ---
    payment_status = models.CharField(
        max_length=20, 
        choices=PAYMENT_STATUS_CHOICES, 
        default='pending',
        verbose_name="Trạng thái thanh toán"
    )
    
    discount_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0, 
        verbose_name="Tổng giảm giá sàn"
    )
    
    shipping_fee = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name="Phí vận chuyển"
    )
    
    notes = models.TextField(null=True, blank=True, verbose_name="Ghi chú")
    # ------------------------------------

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        username = self.buyer.username if self.buyer else "Unknown"
        return f"Order #{self.order_id} - {username}"

class SubOrder(models.Model):
    """
    Đơn hàng con tách theo từng Cửa hàng (Store)
    """
    sub_order_id = models.AutoField(primary_key=True)
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='sub_orders')
    
    # Link tới Store (varchar ID)
    store = models.ForeignKey(
        'store.Store',
        on_delete=models.CASCADE,
        related_name='sales',
        verbose_name="Cửa hàng"
    )
    
    platform_discount = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0, 
        verbose_name="Giảm giá sàn phân bổ"
    )
    # DB datanew dùng cột 'subtotal' thay vì 'total_amount' cho suborder
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Thành tiền")
    
    status = models.CharField(max_length=20, choices=Order.STATUS_CHOICES, default='pending')
    
    platform_discount = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0, 
        verbose_name="Giảm giá sàn phân bổ"
    )
    # Thông tin vận chuyển
    tracking_number = models.CharField(max_length=100, null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"SubOrder #{self.sub_order_id} - {self.store.name}"
    
    def save(self, *args, **kwargs):
        """Override save để tự động update Order status"""
        super().save(*args, **kwargs)
        self._update_parent_order_status()
    
    def _update_parent_order_status(self):
        """Cập nhật trạng thái Order dựa trên SubOrder"""
        order = self.order
        sub_orders = order.sub_orders.all()
        
        if not sub_orders.exists():
            return
        
        statuses = set(sub_orders.values_list('status', flat=True))
        new_status = None
        
        # All completed
        if statuses == {'completed'}:
            new_status = 'completed'
        # All shipped or completed (at least one shipped)
        elif statuses.issubset({'shipped', 'completed'}) and 'shipped' in statuses:
            new_status = 'shipped'
        # At least one processing
        elif 'processing' in statuses:
            new_status = 'processing'
        # Pending is default, no need to explicitly set
        
        if new_status and order.status != new_status:
            order.status = new_status
            order.save(update_fields=['status'])

            # Gửi notification khi trạng thái đơn hàng thay đổi
            from notifications.utils import notify_order_status_update
            try:
                notify_order_status_update(order.buyer, order.order_id, new_status)
            except Exception as e:
                print(f"Notification Error: {str(e)}")

class OrderItem(models.Model):
    # DB datanew dùng 'item_id', code cũ dùng 'order_item_id'
    item_id = models.AutoField(primary_key=True)
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    sub_order = models.ForeignKey(SubOrder, on_delete=models.CASCADE, related_name='items')
    
    variant = models.ForeignKey(
        'products.ProductVariant',
        on_delete=models.PROTECT,
        verbose_name="Biến thể sản phẩm"
    )
    
    quantity = models.IntegerField(default=1)
    price_at_order = models.DecimalField(max_digits=12, decimal_places=2)
    
    # DB datanew có cột này NOT NULL
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.variant.sku} x {self.quantity}"