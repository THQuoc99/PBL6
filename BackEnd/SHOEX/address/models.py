from django.db import models

class Province(models.Model):
    """Bảng quản lý Tỉnh/Thành phố"""
    province_id = models.AutoField(primary_key=True, verbose_name="Mã tỉnh/thành")
    name = models.CharField(max_length=100, unique=True, verbose_name="Tên tỉnh/thành")
    
    class Meta:
        verbose_name = "Tỉnh/Thành phố"
        verbose_name_plural = "Tỉnh/Thành phố"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Ward(models.Model):
    """Bảng quản lý Xã/Phường"""
    ward_id = models.AutoField(primary_key=True, verbose_name="Mã xã/phường")
    province = models.ForeignKey(Province, on_delete=models.CASCADE, related_name='wards', verbose_name="Tỉnh/Thành phố")
    name = models.CharField(max_length=100, verbose_name="Tên xã/phường")
    
    class Meta:
        verbose_name = "Xã/Phường"
        verbose_name_plural = "Xã/Phường"
        ordering = ['province__name', 'name']
        constraints = [
            models.UniqueConstraint(fields=['province', 'name'], name='unique_ward_per_province'),
        ]
    
    def __str__(self):
        return f"{self.name}, {self.province.name}"

class Hamlet(models.Model):
    """Bảng quản lý Thôn/Xóm"""
    hamlet_id = models.AutoField(primary_key=True, verbose_name="Mã thôn/xóm")
    ward = models.ForeignKey(Ward, on_delete=models.CASCADE, related_name='hamlets', verbose_name="Xã/Phường")
    name = models.CharField(max_length=100, verbose_name="Tên thôn/xóm")
    
    class Meta:
        verbose_name = "Thôn/Xóm"
        verbose_name_plural = "Thôn/Xóm"
        ordering = ['ward__name', 'name']
        constraints = [
            models.UniqueConstraint(fields=['ward', 'name'], name='unique_hamlet_per_ward'),
        ]
    
    def __str__(self):
        return f"{self.name}, {self.ward.name}"

class Address(models.Model):
    """Bảng quản lý địa chỉ của người dùng"""
    address_id = models.AutoField(primary_key=True, verbose_name="Mã địa chỉ")
    
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        # ✅ SỬA LỖI: Đổi related_name để tránh trùng lặp với app 'orders'
        related_name='user_addresses', 
        verbose_name="Người dùng"
    )
    
    # ... (Các trường còn lại giữ nguyên: name, phone, province, ward, hamlet, detail, is_default)
    name = models.CharField(max_length=100, default="", verbose_name="Tên người nhận") 
    phone = models.CharField(max_length=20, default="", verbose_name="Số điện thoại") 
    
    province = models.ForeignKey(Province, on_delete=models.PROTECT, verbose_name="Tỉnh/Thành phố")
    ward = models.ForeignKey(Ward, on_delete=models.PROTECT, verbose_name="Xã/Phường")
    hamlet = models.ForeignKey(Hamlet, on_delete=models.PROTECT, null=True, blank=True, verbose_name="Thôn/Xóm")
    
    detail = models.CharField(max_length=255, verbose_name="Địa chỉ chi tiết")
    is_default = models.BooleanField(default=False, verbose_name="Địa chỉ mặc định")
    
    class Meta:
        verbose_name = "Địa chỉ"
        verbose_name_plural = "Địa chỉ"
        ordering = ['-is_default', 'address_id']
    
    def __str__(self):
        return f"{self.name} - {self.detail}"
    
    @property
    def full_address(self):
        parts = [self.detail]
        if self.hamlet: parts.append(self.hamlet.name)
        parts.extend([self.ward.name, self.province.name])
        return ", ".join(parts)
    
    def save(self, *args, **kwargs):
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).exclude(address_id=self.address_id).update(is_default=False)
        super().save(*args, **kwargs)