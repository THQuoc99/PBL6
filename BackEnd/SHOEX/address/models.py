from django.db import models


class Address(models.Model):
    """Bảng quản lý địa chỉ của người dùng"""
    
    address_id = models.AutoField(
        primary_key=True,
        verbose_name="Mã địa chỉ"
    )
    
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='user_addresses',
        verbose_name="Người dùng",
        help_text="Người dùng sở hữu địa chỉ này"
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
        help_text="Đánh dấu là địa chỉ mặc định của người dùng"
    )
    
    class Meta:
        verbose_name = "Địa chỉ"
        verbose_name_plural = "Địa chỉ"
        ordering = ['-is_default', 'address_id']
        constraints = [
            # Đảm bảo mỗi user chỉ có 1 địa chỉ mặc định
            models.UniqueConstraint(
                fields=['user'],
                condition=models.Q(is_default=True),
                name='unique_default_address_per_user'
            ),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.full_address}"
    
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
        """Override save để đảm bảo chỉ có 1 địa chỉ mặc định per user"""
        if self.is_default:
            # Bỏ default của các địa chỉ khác của cùng user
            Address.objects.filter(
                user=self.user,
                is_default=True
            ).exclude(
                address_id=self.address_id
            ).update(is_default=False)
        
        super().save(*args, **kwargs)
    
    def set_as_default(self):
        """Đặt địa chỉ này làm mặc định"""
        # Bỏ default của các địa chỉ khác
        Address.objects.filter(
            user=self.user,
            is_default=True
        ).update(is_default=False)
        
        # Đặt địa chỉ này làm default
        self.is_default = True
        self.save(update_fields=['is_default'])
