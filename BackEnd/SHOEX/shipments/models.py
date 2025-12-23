from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

class Shipment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Chờ lấy hàng'),
        ('picked', 'Đã lấy hàng'),
        ('shipped', 'Đang vận chuyển'),
        ('delivered', 'Giao thành công'),
        ('failed', 'Giao thất bại'),
        ('cancelled', 'Đã hủy'),
    ]

    PICK_OPTION_CHOICES = [
        ('cod', 'Lấy hàng tại nhà'),
        ('post', 'Gửi tại bưu cục'),
    ]

    DELIVER_OPTION_CHOICES = [
        ('standard', 'Tiêu chuẩn'),
        ('fast', 'Hỏa tốc'),
    ]

    shipment_id = models.AutoField(primary_key=True, verbose_name="Mã vận chuyển")
    
    # Map 1-1 với SubOrder (Mỗi đơn hàng con của 1 shop có 1 vận đơn)
    sub_order = models.OneToOneField(
        'orders.SubOrder',
        on_delete=models.CASCADE,
        related_name='shipment',
        verbose_name="Đơn hàng con"
    )
    
    tracking_code = models.CharField(max_length=100, blank=True, null=True, verbose_name="Mã vận đơn")
    
    # Thông tin người gửi (Shop)
    pick_name = models.CharField(max_length=100, verbose_name="Tên người gửi")
    pick_address = models.CharField(max_length=255, verbose_name="Địa chỉ lấy hàng")
    pick_province = models.CharField(max_length=50, verbose_name="Tỉnh/TP gửi")
    pick_ward = models.CharField(max_length=50, verbose_name="Phường/Xã gửi")
    pick_tel = models.CharField(max_length=20, verbose_name="SĐT người gửi")
    
    # Thông tin người nhận (Buyer)
    name = models.CharField(max_length=100, verbose_name="Tên người nhận")
    address = models.CharField(max_length=255, verbose_name="Địa chỉ nhận")
    province = models.CharField(max_length=50, verbose_name="Tỉnh/TP nhận")
    ward = models.CharField(max_length=50, verbose_name="Phường/Xã nhận")
    hamlet = models.CharField(max_length=50, blank=True, null=True, verbose_name="Thôn/Ấp")
    tel = models.CharField(max_length=20, verbose_name="SĐT người nhận")
    
    is_freeship = models.BooleanField(default=False, verbose_name="Freeship")
    pick_date = models.DateField(verbose_name="Ngày lấy dự kiến")
    pick_money = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Tiền thu hộ (COD)")
    
    note = models.TextField(blank=True, null=True, verbose_name="Ghi chú vận chuyển")
    value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Giá trị khai giá")
    
    transport = models.CharField(max_length=50, default='road', verbose_name="Phương thức (Bay/Bộ)")
    pick_option = models.CharField(max_length=10, choices=PICK_OPTION_CHOICES, default='cod')
    deliver_option = models.CharField(max_length=10, choices=DELIVER_OPTION_CHOICES, default='standard')
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name="Trạng thái")
    total_weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Tổng trọng lượng (g)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Vận chuyển"
        verbose_name_plural = "Vận chuyển"
        ordering = ['-created_at']

    def __str__(self):
        return f"Shipment #{self.shipment_id} - {self.tracking_code}"
    
    def save(self, *args, **kwargs):
        """Override save để tự động sync status sang SubOrder"""
        super().save(*args, **kwargs)
        self._sync_status_to_suborder()
    
    def _sync_status_to_suborder(self):
        """Đồng bộ status từ Shipment sang SubOrder
        
        SubOrder STATUS_CHOICES: pending, paid, processing, shipped, completed, cancelled
        """
        status_mapping = {
            'pending': 'paid',         # Chờ lấy → paid (đã thanh toán, chờ lấy hàng)
            'picked': 'processing',    # Đã lấy → processing (đang xử lý/đóng gói)
            'shipped': 'shipped',      # Đang giao → shipped (đang vận chuyển)
            'delivered': 'completed',  # Đã giao → completed
            'failed': 'cancelled',     # Thất bại → cancelled
            'cancelled': 'cancelled',  # Hủy → cancelled
        }
        
        new_status = status_mapping.get(self.status)
        if new_status and self.sub_order.status != new_status:
            self.sub_order.status = new_status
            # Update timestamps
            if self.status == 'shipped':
                self.sub_order.shipped_at = timezone.now()
            elif self.status == 'delivered':
                self.sub_order.delivered_at = timezone.now()
            self.sub_order.save()


class ShipmentTracking(models.Model):
    """Lịch sử hành trình đơn hàng (Webhook từ đơn vị VC)"""
    tracking_id = models.AutoField(primary_key=True)
    
    shipment = models.ForeignKey(
        Shipment, 
        on_delete=models.CASCADE, 
        related_name='tracking_history'
    )
    
    status = models.CharField(max_length=50, verbose_name="Trạng thái VC")
    location = models.CharField(max_length=255, verbose_name="Vị trí")
    details = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(verbose_name="Thời gian sự kiện")
    
    # Thông tin Raw từ API
    carrier_status_code = models.CharField(max_length=50, blank=True, null=True)
    carrier_status_description = models.TextField(blank=True, null=True)
    
    latitude = models.DecimalField(max_digits=10, decimal_places=8, blank=True, null=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, blank=True, null=True)
    estimated_delivery = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    api_response = models.JSONField(blank=True, null=True)
    sync_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-timestamp']
        constraints = [
            models.UniqueConstraint(
                fields=['shipment', 'timestamp', 'status'],
                name='unique_shipment_tracking_status'
            )
        ]

    def __str__(self):
        return f"{self.status} tại {self.location} ({self.timestamp})"

# ==============================================================================
# SIGNALS (Tự động tạo vận đơn)
# ==============================================================================

# Sử dụng string 'orders.SubOrder' để tránh lỗi Circular Import
@receiver(post_save, sender='orders.SubOrder')
def create_shipment_for_suborder(sender, instance, created, **kwargs):
    """
    Tự động tạo Shipment khi SubOrder được tạo
    """
    if created:
        try:
            # Lấy thông tin từ Order cha
            master_order = instance.order
            buyer_address = master_order.address
            
            # Lấy thông tin Store (địa chỉ kho mặc định)
            store = instance.store
            # Giả sử store có quan hệ ngược 'addresses'
            store_address = store.addresses.filter(is_default=True).first()
            
            # Nếu store không có địa chỉ default, lấy cái đầu tiên hoặc để trống
            pick_addr = store_address.detail if store_address else "Kho trung tâm"
            pick_prov = store_address.province if store_address else ""
            pick_ward = store_address.ward if store_address else ""
            
            Shipment.objects.create(
                sub_order=instance,
                
                # Thông tin lấy hàng (Từ Store)
                pick_name=store.name,
                pick_tel=store.phone,
                pick_address=pick_addr,
                pick_province=pick_prov,
                pick_ward=pick_ward,
                
                # Thông tin giao hàng (Từ Buyer Address)
                name=master_order.buyer.full_name,
                tel=master_order.buyer.phone,
                address=buyer_address.detail,
                province=buyer_address.province,
                ward=buyer_address.ward,
                hamlet=buyer_address.hamlet,
                
                # Thông tin đơn
                value=instance.subtotal,
                pick_money=instance.subtotal if master_order.payment_method == 'COD' else 0,
                
                pick_date=timezone.now().date(), # Dự kiến lấy ngay
                status='pending'
            )
        except Exception as e:
            # Log lỗi nếu không tạo được shipment (tránh crash luồng order)
            print(f"Error creating shipment for SubOrder {instance.pk}: {e}")