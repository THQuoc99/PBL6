from django.db import models


class Province(models.Model):
    """Bảng quản lý Tỉnh/Thành phố"""
    
    province_id = models.AutoField(
        primary_key=True,
        verbose_name="Mã tỉnh/thành"
    )
    
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Tên tỉnh/thành",
        help_text="Tên đầy đủ của tỉnh/thành phố"
    )
    
    class Meta:
        verbose_name = "Tỉnh/Thành phố"
        verbose_name_plural = "Tỉnh/Thành phố"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Ward(models.Model):
    """Bảng quản lý Xã/Phường"""
    
    ward_id = models.AutoField(
        primary_key=True,
        verbose_name="Mã xã/phường"
    )
    
    province = models.ForeignKey(
        Province,
        on_delete=models.CASCADE,
        related_name='wards',
        verbose_name="Tỉnh/Thành phố",
        help_text="Tỉnh/thành phố chứa xã/phường này"
    )
    
    name = models.CharField(
        max_length=100,
        verbose_name="Tên xã/phường",
        help_text="Tên đầy đủ của xã/phường"
    )
    
    class Meta:
        verbose_name = "Xã/Phường"
        verbose_name_plural = "Xã/Phường"
        ordering = ['province__name', 'name']
        constraints = [
            models.UniqueConstraint(
                fields=['province', 'name'],
                name='unique_ward_per_province'
            ),
        ]
    
    def __str__(self):
        return f"{self.name}, {self.province.name}"


class Hamlet(models.Model):
    """Bảng quản lý Thôn/Xóm"""
    
    hamlet_id = models.AutoField(
        primary_key=True,
        verbose_name="Mã thôn/xóm"
    )
    
    ward = models.ForeignKey(
        Ward,
        on_delete=models.CASCADE,
        related_name='hamlets',
        verbose_name="Xã/Phường",
        help_text="Xã/phường chứa thôn/xóm này"
    )
    
    name = models.CharField(
        max_length=100,
        verbose_name="Tên thôn/xóm",
        help_text="Tên đầy đủ của thôn/xóm"
    )
    
    class Meta:
        verbose_name = "Thôn/Xóm"
        verbose_name_plural = "Thôn/Xóm"
        ordering = ['ward__name', 'name']
        constraints = [
            models.UniqueConstraint(
                fields=['ward', 'name'],
                name='unique_hamlet_per_ward'
            ),
        ]
    
    def __str__(self):
        return f"{self.name}, {self.ward.name}, {self.ward.province.name}"


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
    
    province = models.ForeignKey(
        Province,
        on_delete=models.CASCADE,
        related_name='addresses',
        verbose_name="Tỉnh/Thành phố",
        help_text="Tỉnh/thành phố của địa chỉ"
    )
    
    ward = models.ForeignKey(
        Ward,
        on_delete=models.CASCADE,
        related_name='addresses',
        verbose_name="Xã/Phường",
        help_text="Xã/phường của địa chỉ"
    )
    
    hamlet = models.ForeignKey(
        Hamlet,
        on_delete=models.CASCADE,
        related_name='addresses',
        null=True,
        blank=True,
        verbose_name="Thôn/Xóm",
        help_text="Thôn/xóm của địa chỉ (có thể để trống)"
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
            parts.append(self.hamlet.name)
        
        parts.extend([
            self.ward.name,
            self.province.name
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
