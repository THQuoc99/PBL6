from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Store(models.Model):
    """Quản lý thông tin cửa hàng"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
    ]
    
    store_id = models.CharField(
        primary_key=True,
        max_length=50,
        verbose_name="Mã cửa hàng"
    )
    
    name = models.CharField(
        max_length=255,
        verbose_name="Tên cửa hàng"
    )
    
    slug = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="URL thân thiện"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Mô tả chi tiết"
    )
    
    email = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Email liên hệ"
    )
    
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Số điện thoại"
    )
    
    address = models.TextField(
        blank=True,
        verbose_name="Địa chỉ chi tiết"
    )
    
    location = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Khu vực"
    )
    
    avatar = models.ImageField(
        upload_to='store/avatars/',
        blank=True,
        null=True,
        verbose_name="Ảnh đại diện"
    )
    
    cover_image = models.ImageField(
        upload_to='store/covers/',
        blank=True,
        null=True,
        verbose_name="Ảnh bìa"
    )
    
    logo = models.ImageField(
        upload_to='store/logos/',
        blank=True,
        null=True,
        verbose_name="Logo"
    )
    
    rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        default=0.0,
        verbose_name="Điểm đánh giá"
    )
    
    total_reviews = models.IntegerField(
        default=0,
        verbose_name="Tổng số đánh giá"
    )
    
    followers_count = models.IntegerField(
        default=0,
        verbose_name="Số người theo dõi"
    )
    
    products_count = models.IntegerField(
        default=0,
        verbose_name="Số sản phẩm"
    )
    
    total_sales = models.IntegerField(
        default=0,
        verbose_name="Tổng đơn hàng đã bán"
    )
    
    total_revenue = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Tổng doanh thu"
    )
    
    is_verified = models.BooleanField(
        default=False,
        verbose_name="Đã xác minh"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Hoạt động"
    )
    
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name="Trạng thái"
    )
    
    response_time = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Thời gian phản hồi"
    )
    
    response_rate = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=0,
        verbose_name="Tỷ lệ phản hồi"
    )
    
    cod_enabled = models.BooleanField(
        default=True,
        verbose_name="Cho phép COD"
    )
    
    express_shipping = models.BooleanField(
        default=True,
        verbose_name="Giao hàng nhanh"
    )
    
    standard_shipping = models.BooleanField(
        default=True,
        verbose_name="Giao hàng thường"
    )
    
    free_shipping_min = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Miễn phí ship từ"
    )
    
    return_policy = models.TextField(
        blank=True,
        verbose_name="Chính sách đổi trả"
    )
    
    shipping_policy = models.TextField(
        blank=True,
        verbose_name="Chính sách vận chuyển"
    )
    
    warranty_policy = models.TextField(
        blank=True,
        verbose_name="Chính sách bảo hành"
    )
    
    currency = models.CharField(
        max_length=5,
        default='VND',
        verbose_name="Đơn vị tiền tệ"
    )
    
    timezone = models.CharField(
        max_length=50,
        default='Asia/Ho_Chi_Minh',
        verbose_name="Múi giờ"
    )
    
    join_date = models.DateTimeField(
        verbose_name="Ngày tham gia"
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
        verbose_name = "Cửa hàng"
        verbose_name_plural = "Cửa hàng"
    
    def __str__(self):
        return self.name


class StoreUser(models.Model):
    """Quản lý thành viên cửa hàng và phân quyền"""
    
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('employee', 'Employee'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('pending', 'Pending'),
    ]
    
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name='store_users',
        verbose_name="Cửa hàng"
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='store_memberships',
        verbose_name="Người dùng"
    )
    
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        verbose_name="Vai trò"
    )
    
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Trạng thái"
    )
    
    granted_permissions = models.JSONField(
        blank=True,
        null=True,
        verbose_name="Quyền bổ sung được cấp"
    )
    
    revoked_permissions = models.JSONField(
        blank=True,
        null=True,
        verbose_name="Quyền bị thu hồi"
    )
    
    invited_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sent_invitations',
        verbose_name="Người mời"
    )
    
    invited_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Thời gian được mời"
    )
    
    joined_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Thời gian tham gia"
    )
    
    last_login = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Lần đăng nhập cuối"
    )
    
    notes = models.TextField(
        blank=True,
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
        verbose_name = "Thành viên cửa hàng"
        verbose_name_plural = "Thành viên cửa hàng"
        constraints = [
            models.UniqueConstraint(
                fields=['store', 'user'],
                name='unique_store_user'
            ),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.store.name} ({self.get_role_display()})"


class StoreCategory(models.Model):
    """Liên kết Store với Category"""
    
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name='store_categories',
        verbose_name="Cửa hàng"
    )
    
    category = models.ForeignKey(
        'products.Category',
        on_delete=models.CASCADE,
        related_name='store_categories',
        verbose_name="Danh mục"
    )
    
    is_primary = models.BooleanField(
        default=False,
        verbose_name="Danh mục chính"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Ngày tạo"
    )
    
    class Meta:
        verbose_name = "Danh mục cửa hàng"
        verbose_name_plural = "Danh mục cửa hàng"
        constraints = [
            models.UniqueConstraint(
                fields=['store', 'category'],
                name='unique_store_category'
            ),
        ]
    
    def __str__(self):
        return f"{self.store.name} - {self.category.name}"


class StoreReview(models.Model):
    """Đánh giá cửa hàng"""
    
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name="Cửa hàng"
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='store_reviews',
        verbose_name="Người đánh giá"
    )
    
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='store_reviews',
        verbose_name="Đơn hàng liên quan"
    )
    
    rating = models.IntegerField(
        verbose_name="Điểm đánh giá"
    )
    
    title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Tiêu đề"
    )
    
    comment = models.TextField(
        blank=True,
        verbose_name="Nội dung đánh giá"
    )
    
    images = models.JSONField(
        blank=True,
        null=True,
        verbose_name="Ảnh đính kèm"
    )
    
    helpful_count = models.IntegerField(
        default=0,
        verbose_name="Số lượt hữu ích"
    )
    
    is_verified = models.BooleanField(
        default=False,
        verbose_name="Đánh giá đã xác thực"
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
        verbose_name = "Đánh giá cửa hàng"
        verbose_name_plural = "Đánh giá cửa hàng"
    
    def __str__(self):
        return f"{self.user.username} - {self.store.name} ({self.rating}/5)"


class StoreFollower(models.Model):
    """Người theo dõi cửa hàng"""
    
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name="Cửa hàng"
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followed_stores',
        verbose_name="Người theo dõi"
    )
    
    followed_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Thời gian theo dõi"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Còn theo dõi"
    )
    
    class Meta:
        verbose_name = "Người theo dõi"
        verbose_name_plural = "Người theo dõi"
        constraints = [
            models.UniqueConstraint(
                fields=['store', 'user'],
                name='unique_store_follower'
            ),
        ]
    
    def __str__(self):
        return f"{self.user.username} follows {self.store.name}"


class StoreAnalytics(models.Model):
    """Thống kê cửa hàng"""
    
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name='analytics',
        verbose_name="Cửa hàng"
    )
    
    date = models.DateField(
        verbose_name="Ngày thống kê"
    )
    
    views = models.IntegerField(
        default=0,
        verbose_name="Lượt xem"
    )
    
    visitors = models.IntegerField(
        default=0,
        verbose_name="Khách truy cập"
    )
    
    orders = models.IntegerField(
        default=0,
        verbose_name="Đơn hàng"
    )
    
    revenue = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Doanh thu"
    )
    
    new_followers = models.IntegerField(
        default=0,
        verbose_name="Người theo dõi mới"
    )
    
    products_added = models.IntegerField(
        default=0,
        verbose_name="Sản phẩm thêm mới"
    )
    
    class Meta:
        verbose_name = "Thống kê cửa hàng"
        verbose_name_plural = "Thống kê cửa hàng"
        constraints = [
            models.UniqueConstraint(
                fields=['store', 'date'],
                name='unique_store_analytics_date'
            ),
        ]
    
    def __str__(self):
        return f"{self.store.name} - {self.date}"


class StoreSettings(models.Model):
    """Cài đặt cửa hàng"""
    
    store = models.OneToOneField(
        Store,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='settings',
        verbose_name="Cửa hàng"
    )
    
    auto_confirm_orders = models.BooleanField(
        default=False,
        verbose_name="Tự động xác nhận đơn"
    )
    
    notification_email = models.BooleanField(
        default=True,
        verbose_name="Thông báo email"
    )
    
    notification_sms = models.BooleanField(
        default=False,
        verbose_name="Thông báo SMS"
    )
    
    working_hours_start = models.TimeField(
        blank=True,
        null=True,
        verbose_name="Giờ làm việc bắt đầu"
    )
    
    working_hours_end = models.TimeField(
        blank=True,
        null=True,
        verbose_name="Giờ làm việc kết thúc"
    )
    
    working_days = models.JSONField(
        blank=True,
        null=True,
        verbose_name="Ngày làm việc"
    )
    
    vacation_mode = models.BooleanField(
        default=False,
        verbose_name="Chế độ nghỉ phép"
    )
    
    vacation_message = models.TextField(
        blank=True,
        verbose_name="Thông báo nghỉ phép"
    )
    
    auto_reply_message = models.TextField(
        blank=True,
        verbose_name="Tin nhắn tự động"
    )
    
    class Meta:
        verbose_name = "Cài đặt cửa hàng"
        verbose_name_plural = "Cài đặt cửa hàng"
    
    def __str__(self):
        return f"Settings for {self.store.name}"


class StoreImage(models.Model):
    """Hình ảnh cửa hàng"""
    
    IMAGE_TYPE_CHOICES = [
        ('cover', 'Cover'),
        ('gallery', 'Gallery'),
        ('logo', 'Logo'),
        ('banner', 'Banner'),
    ]
    
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name="Cửa hàng"
    )
    
    image = models.ImageField(
        upload_to='store/gallery/',
        verbose_name="Hình ảnh"
    )
    
    image_type = models.CharField(
        max_length=10,
        choices=IMAGE_TYPE_CHOICES,
        verbose_name="Loại hình ảnh"
    )
    
    title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Tiêu đề"
    )
    
    alt_text = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Mô tả"
    )
    
    sort_order = models.IntegerField(
        default=0,
        verbose_name="Thứ tự sắp xếp"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Đang sử dụng"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Ngày tạo"
    )
    
    class Meta:
        verbose_name = "Hình ảnh cửa hàng"
        verbose_name_plural = "Hình ảnh cửa hàng"
    
    def __str__(self):
        return f"{self.store.name} - {self.get_image_type_display()}"


class StoreRole(models.Model):
    """Vai trò cửa hàng"""
    
    role_name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Tên vai trò"
    )
    
    role_display_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Tên hiển thị"
    )
    
    description = models.TextField(
        blank=True,
        verbose_name="Mô tả vai trò"
    )
    
    default_permissions = models.JSONField(
        blank=True,
        null=True,
        verbose_name="Quyền mặc định"
    )
    
    is_system_role = models.BooleanField(
        default=True,
        verbose_name="Vai trò hệ thống"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Ngày tạo"
    )
    
    class Meta:
        verbose_name = "Vai trò cửa hàng"
        verbose_name_plural = "Vai trò cửa hàng"
    
    def __str__(self):
        return self.role_display_name or self.role_name


class StorePermission(models.Model):
    """Quyền hạn cửa hàng"""
    
    permission_name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Tên quyền"
    )
    
    permission_group = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Nhóm quyền"
    )
    
    display_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Tên hiển thị"
    )
    
    description = models.TextField(
        blank=True,
        verbose_name="Mô tả quyền"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Còn sử dụng"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Ngày tạo"
    )
    
    class Meta:
        verbose_name = "Quyền hạn cửa hàng"
        verbose_name_plural = "Quyền hạn cửa hàng"
    
    def __str__(self):
        return self.display_name or self.permission_name


class StoreInvitation(models.Model):
    """Lời mời tham gia cửa hàng"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('expired', 'Expired'),
        ('revoked', 'Revoked'),
    ]
    
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name='invitations',
        verbose_name="Cửa hàng"
    )
    
    email = models.CharField(
        max_length=255,
        verbose_name="Email được mời"
    )
    
    role = models.CharField(
        max_length=50,
        verbose_name="Vai trò được mời"
    )
    
    invitation_token = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="Token xác thực"
    )
    
    invited_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_store_invitations',
        verbose_name="Người gửi lời mời"
    )
    
    invited_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Thời gian gửi"
    )
    
    expires_at = models.DateTimeField(
        verbose_name="Thời gian hết hạn"
    )
    
    accepted_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Thời gian chấp nhận"
    )
    
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Trạng thái"
    )
    
    message = models.TextField(
        blank=True,
        verbose_name="Tin nhắn mời"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Ngày tạo"
    )
    
    class Meta:
        verbose_name = "Lời mời tham gia"
        verbose_name_plural = "Lời mời tham gia"
    
    def __str__(self):
        return f"Invitation to {self.email} for {self.store.name}"


class AddressStore(models.Model):
    """Bảng quản lý địa chỉ của cửa hàng"""

    address_id = models.AutoField(
        primary_key=True,
        verbose_name="Mã địa chỉ"
    )

    store = models.ForeignKey(
        'Store',
        on_delete=models.CASCADE,
        related_name='addresses',
        verbose_name="Cửa hàng",
        help_text="Cửa hàng sở hữu địa chỉ này"
    )

    province = models.CharField(
        max_length=100,
        verbose_name="Tỉnh/Thành phố",
        help_text="Tên tỉnh/thành phố"
    )

    ward = models.CharField(
        max_length=100,
        verbose_name="Xã/Phường",
        help_text="Tên xã/phường"
    )

    hamlet = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Thôn/Xóm",
        help_text="Tên thôn/xóm (có thể để trống)"
    )

    detail = models.CharField(
        max_length=255,
        verbose_name="Địa chỉ chi tiết",
        help_text="Số nhà, ngõ, đường, v.v."
    )

    is_default = models.BooleanField(
        default=False,
        verbose_name="Địa chỉ mặc định",
        help_text="Đánh dấu là địa chỉ mặc định của cửa hàng"
    )

    class Meta:
        verbose_name = "Địa chỉ cửa hàng"
        verbose_name_plural = "Địa chỉ cửa hàng"
        ordering = ['-is_default', 'address_id']
        constraints = [
            # Đảm bảo mỗi store chỉ có 1 địa chỉ mặc định
            models.UniqueConstraint(
                fields=['store'],
                condition=models.Q(is_default=True),
                name='unique_default_address_per_store'
            ),
        ]

    def __str__(self):
        return f"{self.store.name} - {self.full_address}"

    @property
    def full_address(self):
        """Trả về địa chỉ đầy đủ"""
        parts = [self.detail]
        if self.hamlet:
            parts.append(self.hamlet)
        parts.extend([
            self.ward,
            self.province
        ])
        return ", ".join(parts)

    def save(self, *args, **kwargs):
        """Override save để đảm bảo chỉ có 1 địa chỉ mặc định per store"""
        if self.is_default:
            AddressStore.objects.filter(
                store=self.store,
                is_default=True
            ).exclude(
                address_id=self.address_id
            ).update(is_default=False)
        super().save(*args, **kwargs)

    def set_as_default(self):
        """Đặt địa chỉ này làm mặc định"""
        AddressStore.objects.filter(
            store=self.store,
            is_default=True
        ).update(is_default=False)
        self.is_default = True
        self.save(update_fields=['is_default'])
