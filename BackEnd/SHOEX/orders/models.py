from django.db import models
from address.models import Address


class Order(models.Model):
    """Đơn hàng chính"""
    
    STATUS_CHOICES = [
        ('pending', 'Đang chờ'),
        ('confirmed', 'Đã xác nhận'),
        ('processing', 'Đang xử lý'),
        ('shipped', 'Đã gửi hàng'),
        ('delivered', 'Đã giao hàng'),
        ('cancelled', 'Đã hủy'),
        ('returned', 'Đã trả hàng'),
    ]

    order_id = models.AutoField(
        primary_key=True,
        verbose_name="Mã đơn hàng"
    )
    
    buyer = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name="Người mua"
    )
    
    address = models.ForeignKey(
        Address,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name="Địa chỉ giao hàng"
    )
    
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Tổng tiền"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Trạng thái đơn hàng"
    )
    
    # Thông tin thanh toán
    payment_method = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Phương thức thanh toán"
    )
    
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Chờ thanh toán'),
            ('paid', 'Đã thanh toán'),
            ('failed', 'Thanh toán thất bại'),
            ('refunded', 'Đã hoàn tiền'),
        ],
        default='pending',
        verbose_name="Trạng thái thanh toán"
    )
    
    shipping_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="Phí vận chuyển"
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Ghi chú"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Ngày tạo"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Ngày cập nhật"
    )

    class Meta:
        verbose_name = "Đơn hàng"
        verbose_name_plural = "Đơn hàng"
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Order #{self.order_id} - {self.buyer.email}"


class SubOrder(models.Model):
    """Đơn hàng con (theo store)"""

    sub_order_id = models.AutoField(
        primary_key=True,
        verbose_name="Mã đơn hàng con"
    )
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='sub_orders',
        verbose_name="Đơn hàng chính"
    )
    
    store = models.ForeignKey(
        'store.Store',
        on_delete=models.CASCADE,
        related_name='sub_orders',
        verbose_name="Cửa hàng"
    )
    
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Tổng tiền con"
    )
    
    status = models.CharField(
        max_length=20,
        choices=Order.STATUS_CHOICES,
        default='pending',
        verbose_name="Trạng thái"
    )
    
    tracking_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Mã vận đơn"
    )
    
    shipped_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Ngày gửi hàng"
    )
    
    delivered_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Ngày giao hàng"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Ngày tạo"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Ngày cập nhật"
    )

    class Meta:
        verbose_name = "Đơn hàng con"
        verbose_name_plural = "Đơn hàng con"
        
    def __str__(self):
        return f"SubOrder #{self.sub_order_id} - {self.store.name}"


class OrderItem(models.Model):
    """Mục trong đơn hàng"""
    
    item_id = models.AutoField(
        primary_key=True,
        verbose_name="Mã mục"
    )
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='order_items',
        verbose_name="Đơn hàng"
    )
    
    sub_order = models.ForeignKey(
        SubOrder,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Đơn hàng con"
    )
    
    variant = models.ForeignKey(
        'products.ProductVariant',
        on_delete=models.CASCADE,
        related_name='order_items',
        verbose_name="Biến thể sản phẩm"
    )
    
    quantity = models.PositiveIntegerField(
        verbose_name="Số lượng"
    )
    
    price_at_order = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Giá tại thời điểm đặt hàng"
    )
    
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="Số tiền giảm giá"
    )
    
    class Meta:
        verbose_name = "Mục đơn hàng"
        verbose_name_plural = "Mục đơn hàng"
        
    def __str__(self):
        return f"{self.variant.product.name} x{self.quantity}"
    
    @property
    def subtotal(self):
        return (self.quantity * self.price_at_order) - self.discount_amount
