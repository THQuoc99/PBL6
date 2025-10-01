from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Province(models.Model):
    """Bảng quản lý Tỉnh/Thành phố"""
    
    province_id = models.IntegerField(
        primary_key=True,
        verbose_name="Mã tỉnh/thành"
    )
    
    name = models.CharField(
        max_length=100,
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
    """Bảng quản lý Xã/Phường - liên kết trực tiếp với Tỉnh"""
    
    ward_id = models.IntegerField(
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


class Address(models.Model):
    """Bảng quản lý địa chỉ của người dùng - Cấu trúc 2 cấp"""
    
    address_id = models.AutoField(
        primary_key=True,
        verbose_name="Mã địa chỉ"
    )
    
    user = models.ForeignKey(
        User, 
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
    
    specific_address = models.TextField(
        verbose_name="Địa chỉ cụ thể",
        help_text="Số nhà, tên đường, địa chỉ chi tiết"
    )
    
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name="Số điện thoại",
        help_text="Số điện thoại liên hệ tại địa chỉ này"
    )
    
    recipient_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Tên người nhận",
        help_text="Tên người nhận hàng tại địa chỉ này"
    )
    
    is_default = models.BooleanField(
        default=False,
        verbose_name="Địa chỉ mặc định",
        help_text="Đánh dấu địa chỉ này là mặc định"
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Ghi chú",
        help_text="Ghi chú thêm về địa chỉ (cách tìm, landmark...)"
    )

    class Meta:
        verbose_name = "Địa chỉ"
        verbose_name_plural = "Địa chỉ"
        ordering = ['address_id']
        constraints = [
            # Mỗi user chỉ có 1 địa chỉ mặc định
            models.UniqueConstraint(
                fields=['user'],
                condition=models.Q(is_default=True),
                name='unique_default_address_per_user'
            ),
        ]
    
    def __str__(self):
        return f"{self.specific_address}, {self.ward.name}, {self.province.name}"
    
    @property
    def full_address(self):
        """Địa chỉ đầy đủ"""
        return f"{self.specific_address}, {self.ward.name}, {self.province.name}"
    
    def save(self, *args, **kwargs):
        """Override save để đảm bảo logic default address"""
        # Kiểm tra ward có thuộc province không
        if self.ward.province != self.province:
            raise ValueError(f"Xã/phường {self.ward.name} không thuộc {self.province.name}")
        
        # Xử lý default address
        if self.is_default:
            # Bỏ default của các địa chỉ khác của user này
            Address.objects.filter(
                user=self.user,
                is_default=True
            ).exclude(
                address_id=self.address_id
            ).update(is_default=False)
        
        super().save(*args, **kwargs)
    
    def set_as_default(self):
        """Đặt địa chỉ này làm mặc định"""
        # Bỏ default của tất cả địa chỉ khác của user
        Address.objects.filter(user=self.user).update(is_default=False)
        
        # Đặt địa chỉ này làm default
        self.is_default = True
        self.save(update_fields=['is_default'])

    @classmethod
    def get_user_default_address(cls, user):
        """Lấy địa chỉ mặc định của user"""
        try:
            return cls.objects.get(user=user, is_default=True)
        except cls.DoesNotExist:
            # Nếu không có default, lấy địa chỉ đầu tiên
            return cls.objects.filter(user=user).first()
    
    @classmethod
    def get_addresses_by_province(cls, province):
        """Lấy tất cả địa chỉ trong tỉnh"""
        return cls.objects.filter(province=province)
    
    @classmethod
    def get_addresses_by_ward(cls, ward):
        """Lấy tất cả địa chỉ trong xã/phường"""
        return cls.objects.filter(ward=ward)


# Utility functions để import dữ liệu
def import_provinces_from_json(json_file_path):
    """Import provinces từ file JSON"""
    import json
    
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    provinces_data = data.get('provinces', [])
    
    for province_data in provinces_data:
        Province.objects.get_or_create(
            province_id=province_data['province_id'],
            defaults={'name': province_data['name']}
        )
    
    print(f"Imported {len(provinces_data)} provinces")


def import_wards_from_json(json_file_path):
    """Import wards từ file JSON"""
    import json
    
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    wards_data = data.get('wards', [])
    
    for ward_data in wards_data:
        try:
            province = Province.objects.get(province_id=ward_data['province_id'])
            Ward.objects.get_or_create(
                ward_id=ward_data['ward_id'],
                defaults={
                    'province': province,
                    'name': ward_data['name']
                }
            )
        except Province.DoesNotExist:
            print(f"Province {ward_data['province_id']} not found for ward {ward_data['name']}")
    
    print(f"Imported {len(wards_data)} wards")