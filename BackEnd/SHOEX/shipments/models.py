from django.db import models

class Shipment(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Chờ xác nhận'),
        ('shipping', 'Vận chuyển'),
        ('out_for_delivery', 'Chờ giao hàng'),
        ('completed', 'Hoàn thành'),
        ('cancelled', 'Đã hủy'),
        ('returned', 'Trả hàng / Hoàn tiền'),
    ]
    PICK_OPTION_CHOICES = [
            # 'cod' ở đây được hiểu là 'Shop muốn nhân viên đến lấy hàng' (Pick-up by Courier)
            ('cod', 'Nhân viên đến lấy hàng (Courier Pick-up)'),
            # 'post' được hiểu là 'Shop tự mang ra bưu cục gửi' (Drop-off at Post Office)
            ('post', 'Gửi tại Bưu cục (Drop-off)'), 
        ]
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='shipments',
        verbose_name="Người mua"
    )
    store = models.ForeignKey(
        'store.Store',
        on_delete=models.CASCADE,
        related_name='shipments',
        verbose_name="Cửa hàng"
    )
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
    pick_date = models.DateField(
        verbose_name="Ngày lấy hàng",
        help_text="Ngày lấy hàng từ người gửi",
        blank=True,
        null=True,
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
    status = models.CharField(
        max_length=100,
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
    Lưu các mốc tracking trả về từ API hãng vận chuyển (GHTK)
    """

    id = models.AutoField(primary_key=True)

    shipment = models.ForeignKey(
        Shipment,
        on_delete=models.CASCADE,
        related_name='trackings'
    )

    # ===== GIỐNG API GHTK =====
    label_id = models.CharField(
        max_length=100,
        verbose_name="Mã vận đơn GHTK"
    )

    partner_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Mã đơn phía hệ thống"
    )
    carrier_status = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Mã trạng thái từ hãng"
    )

    carrier_status_text = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Mô tả trạng thái từ hãng"
    )

    message = models.TextField(
        blank=True,
        null=True,
        verbose_name="Thông báo từ hãng"
    )

    # ===== THỜI GIAN =====
    event_time = models.DateTimeField(
        verbose_name="Thời điểm trạng thái (API)",
        blank=True,
        null=True,
    )

    synced_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Thời điểm hệ thống lưu"
    )

    # ===== DỮ LIỆU PHÁT SINH =====
    weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )

    # Estimated times returned by carrier (human-readable)
    estimated_pick_time = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Thời gian dự kiến lấy hàng",
        help_text='Ví dụ: "Sáng 2025-12-18"'
    )

    estimated_deliver_time = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Thời gian dự kiến giao hàng",
        help_text='Ví dụ: "Sáng 2025-12-19"'
    )
    



    raw_response = models.JSONField(
        verbose_name="Raw API response"
    )

    class Meta:
        ordering = ['-event_time']
        indexes = [
            models.Index(fields=['shipment']),
            models.Index(fields=['label_id']),
            models.Index(fields=['carrier_status']),
            models.Index(fields=['event_time']),
        ]

    def __str__(self):
        return f"{self.label_id} - {self.carrier_status_text}"
