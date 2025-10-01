from django.db import models

class Shipment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('picked', 'Picked'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
    ]

    PICK_OPTION_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('non_cod', 'Non-Cash on Delivery'),
    ]

    DELIVER_OPTION_CHOICES = [
        ('xteam', 'Xteam'),
        ('standard', 'Standard'),
    ]

    shipment_id = models.AutoField(
        primary_key=True,
        verbose_name="Mã vận chuyển",
        help_text="ID tự tăng, duy nhất cho mỗi vận chuyển"
    )
    sub_order = models.OneToOneField(
        'orders.SubOrder',
        on_delete=models.CASCADE,
        related_name='shipment',
        verbose_name="Đơn hàng con",
        help_text="Đơn hàng con liên kết với vận chuyển này"
    )                                                                                           
    tracking_code = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Mã theo dõi",
        help_text="Mã theo dõi vận chuyển (nếu có)"
    )
    pick_name = models.CharField(
        max_length=100,
        verbose_name="Tên người gửi",
        help_text="Tên của người gửi hàng"
    )
    pick_address = models.CharField(
        max_length=255,
        verbose_name="Địa chỉ người gửi",
        help_text="Địa chỉ của người gửi hàng"
    )
    pick_province = models.CharField(
        max_length=50,
        verbose_name="Tỉnh người gửi",
        help_text="Tỉnh nơi người gửi hàng"
    )
    pick_ward = models.CharField(
        max_length=50,
        verbose_name="Phường/Xã người gửi",
        help_text="Phường/Xã nơi người gửi hàng"
    )
    pick_tel = models.CharField(
        max_length=20,
        verbose_name="Số điện thoại người gửi",
        help_text="Số điện thoại của người gửi hàng"
    )
    name = models.CharField(
        max_length=100,
        verbose_name="Tên người nhận",
        help_text="Tên của người nhận hàng"
    )
    address = models.CharField(
        max_length=255,
        verbose_name="Địa chỉ người nhận",
        help_text="Địa chỉ của người nhận hàng"
    )
    province = models.CharField(
        max_length=50,
        verbose_name="Tỉnh người nhận",
        help_text="Tỉnh nơi người nhận hàng"
    )
    ward = models.CharField(
        max_length=50,
        verbose_name="Phường/Xã người nhận",
        help_text="Phường/Xã nơi người nhận hàng"
    )
    hamlet = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Thôn/Ấp người nhận",
        help_text="Thôn/Ấp nơi người nhận hàng (nếu có)"
    )
    tel = models.CharField(
        max_length=20,
        verbose_name="Số điện thoại người nhận",
        help_text="Số điện thoại của người nhận hàng"
    )
    is_freeship = models.BooleanField(
        default=False,
        verbose_name="Miễn phí vận chuyển",
        help_text="Đánh dấu nếu vận chuyển miễn phí"
    )
    pick_date = models.DateField(
        verbose_name="Ngày lấy hàng",
        help_text="Ngày lấy hàng từ người gửi"
    )
    pick_money = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="Tiền thu hộ",
        help_text="Số tiền thu hộ từ người nhận"
    )
    note = models.TextField(
        blank=True,
        null=True,
        verbose_name="Ghi chú",
        help_text="Ghi chú thêm về vận chuyển"
    )
    value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Giá trị hàng hóa",
        help_text="Tổng giá trị của hàng hóa vận chuyển"
    )
    transport = models.CharField(
        max_length=50,
        verbose_name="Phương tiện vận chuyển",
        help_text="Phương tiện được sử dụng để vận chuyển"
    )
    pick_option = models.CharField(
        max_length=10,
        choices=PICK_OPTION_CHOICES,
        default='cod',
        verbose_name="Tùy chọn lấy hàng",
        help_text="Tùy chọn lấy hàng (COD hoặc không COD)"
    )
    deliver_option = models.CharField(
        max_length=10,
        choices=DELIVER_OPTION_CHOICES,
        default='standard',
        verbose_name="Tùy chọn giao hàng",
        help_text="Tùy chọn giao hàng (Xteam hoặc Standard)"
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Trạng thái vận chuyển",
        help_text="Trạng thái hiện tại của vận chuyển"
    )
    total_weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Tổng khối lượng",
        help_text="Tổng khối lượng của hàng hóa vận chuyển"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Ngày tạo",
        help_text="Ngày giờ vận chuyển được tạo"
    )
    updated_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Ngày cập nhật",
        help_text="Ngày giờ vận chuyển được cập nhật"
    )

    def __str__(self):
        return f"Shipment {self.shipment_id} - {self.status}"

    class Meta:
        verbose_name = "Vận chuyển"
        verbose_name_plural = "Vận chuyển"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sub_order']),
            models.Index(fields=['tracking_code']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]


class ShipmentTracking(models.Model):
    """
    Bảng lưu chi tiết lộ trình vận chuyển
    Theo dõi các mốc trạng thái và vị trí từ API tracking
    """
    
    STATUS_CHOICES = [
        ('created', 'Created'),
        ('picked_up', 'Picked Up'),
        ('in_transit', 'In Transit'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('failed_delivery', 'Failed Delivery'),
        ('returned', 'Returned'),
        ('cancelled', 'Cancelled'),
        ('exception', 'Exception'),
    ]
    
    tracking_id = models.AutoField(
        primary_key=True,
        verbose_name="ID tracking",
        help_text="ID duy nhất của bản ghi tracking"
    )
    
    shipment = models.ForeignKey(
        Shipment,
        on_delete=models.CASCADE,
        related_name='tracking_history',
        verbose_name="Vận chuyển",
        help_text="Shipment liên kết với tracking này"
    )
    
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        verbose_name="Trạng thái lộ trình",
        help_text="Trạng thái hiện tại trong lộ trình vận chuyển"
    )
    
    location = models.CharField(
        max_length=255,
        verbose_name="Vị trí hiện tại",
        help_text="Vị trí hiện tại của đơn hàng"
    )
    
    details = models.TextField(
        blank=True,
        null=True,
        verbose_name="Chi tiết trạng thái",
        help_text="Mô tả cụ thể về trạng thái hiện tại"
    )
    
    timestamp = models.DateTimeField(
        verbose_name="Thời gian sự kiện",
        help_text="Thời gian xảy ra sự kiện trong lộ trình"
    )
    
    # Thông tin bổ sung từ API tracking
    carrier_status_code = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Mã trạng thái nhà vận chuyển",
        help_text="Mã trạng thái gốc từ API nhà vận chuyển"
    )
    
    carrier_status_description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Mô tả trạng thái nhà vận chuyển",
        help_text="Mô tả trạng thái gốc từ nhà vận chuyển"
    )
    
    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=8,
        blank=True,
        null=True,
        verbose_name="Vĩ độ",
        help_text="Tọa độ vĩ độ của vị trí (nếu có)"
    )
    
    longitude = models.DecimalField(
        max_digits=11,
        decimal_places=8,
        blank=True,
        null=True,
        verbose_name="Kinh độ",
        help_text="Tọa độ kinh độ của vị trí (nếu có)"
    )
    
    estimated_delivery = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Thời gian giao hàng dự kiến",
        help_text="Thời gian giao hàng dự kiến được cập nhật"
    )
    
    # Metadata
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Thời gian lưu bản ghi",
        help_text="Thời gian bản ghi tracking được tạo trong hệ thống"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Thời gian cập nhật",
        help_text="Thời gian bản ghi được cập nhật lần cuối"
    )
    
    # Thông tin sync từ API
    api_response = models.JSONField(
        blank=True,
        null=True,
        verbose_name="Raw API Response",
        help_text="Phản hồi gốc từ API tracking (để debug)"
    )
    
    sync_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Thời gian đồng bộ",
        help_text="Thời gian đồng bộ dữ liệu từ API"
    )
    
    class Meta:
        verbose_name = "Lịch sử theo dõi vận chuyển"
        verbose_name_plural = "Lịch sử theo dõi vận chuyển"
        ordering = ['-timestamp', '-created_at']
        indexes = [
            models.Index(fields=['shipment', 'timestamp']),
            models.Index(fields=['status']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['created_at']),
            models.Index(fields=['sync_at']),
        ]
        constraints = [
            # Đảm bảo không có duplicate tracking cho cùng shipment tại cùng thời điểm
            models.UniqueConstraint(
                fields=['shipment', 'timestamp', 'status'],
                name='unique_shipment_tracking_status'
            ),
        ]
    
    def __str__(self):
        return f"Tracking {self.tracking_id} - {self.shipment.shipment_id} - {self.status}"
    
    @property
    def status_display_vietnamese(self):
        """Hiển thị trạng thái bằng tiếng Việt"""
        status_map = {
            'created': 'Đã tạo đơn',
            'picked_up': 'Đã lấy hàng',
            'in_transit': 'Đang vận chuyển',
            'out_for_delivery': 'Đang giao hàng',
            'delivered': 'Đã giao hàng',
            'failed_delivery': 'Giao hàng thất bại',
            'returned': 'Đã trả về',
            'cancelled': 'Đã hủy',
            'exception': 'Có vấn đề',
        }
        return status_map.get(self.status, self.status)
    
    @property
    def has_location_coordinates(self):
        """Kiểm tra có tọa độ vị trí không"""
        return self.latitude is not None and self.longitude is not None
    
    @property
    def is_final_status(self):
        """Kiểm tra có phải trạng thái cuối cùng không"""
        final_statuses = ['delivered', 'returned', 'cancelled']
        return self.status in final_statuses
    
    @property
    def is_in_progress(self):
        """Kiểm tra có đang trong quá trình vận chuyển không"""
        progress_statuses = ['created', 'picked_up', 'in_transit', 'out_for_delivery']
        return self.status in progress_statuses
    
    def save(self, *args, **kwargs):
        """Override save để cập nhật trạng thái shipment"""
        super().save(*args, **kwargs)
        
        # Cập nhật trạng thái shipment nếu cần
        if self.is_final_status:
            shipment = self.shipment
            if self.status == 'delivered':
                shipment.status = 'delivered'
            elif self.status in ['returned', 'cancelled']:
                shipment.status = 'failed'
            shipment.save(update_fields=['status', 'updated_at'])