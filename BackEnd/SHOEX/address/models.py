from django.db import models
from django.db.models import Q

class Address(models.Model):
    """
    Bảng quản lý địa chỉ của người dùng.
    Map với bảng: public.address_address
    """
    name = models.CharField(max_length=100, default="", verbose_name="Tên người nhận")
    phone = models.CharField(max_length=20, default="", verbose_name="Số điện thoại")
    address_id = models.AutoField(
        primary_key=True,
        verbose_name="Mã địa chỉ"
    )
    
    # Khớp với user_id bigint NOT NULL
    user = models.ForeignKey(
        'users.User',  # Giả sử app user của bạn tên là 'users'
        on_delete=models.CASCADE,
        related_name='user_addresses',
        verbose_name="Người dùng",
        db_column='user_id' # Chỉ định rõ cột trong DB
    )
    
    # Khớp với province character varying(100) NOT NULL
    province = models.CharField(
        max_length=100,
        verbose_name="Tỉnh/Thành phố"
    )
    
    # Khớp với ward character varying(100) NOT NULL
    ward = models.CharField(
        max_length=100,
        verbose_name="Xã/Phường" # Lưu ý: DB mới không còn cột District (Huyện), Ward thường chứa cả thông tin huyện hoặc bạn cần check lại logic nhập liệu
    )
    
    # Khớp với hamlet character varying(100) (Có thể null trong SQL)
    hamlet = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Thôn/Xóm/Quận/Huyện" 
    )
    
    # Khớp với detail character varying(255) NOT NULL
    detail = models.CharField(
        max_length=255,
        verbose_name="Địa chỉ chi tiết"
    )
    
    # Khớp với is_default boolean NOT NULL
    is_default = models.BooleanField(
        default=False,
        verbose_name="Địa chỉ mặc định"
    )

    class Meta:
        db_table = 'address_address'  # Map chính xác tên bảng trong datanew.sql
        verbose_name = "Địa chỉ người dùng"
        verbose_name_plural = "Danh sách địa chỉ"
        ordering = ['-is_default', '-address_id']
        constraints = [
            # Map với INDEX: unique_default_address_per_user
            models.UniqueConstraint(
                fields=['user'],
                condition=Q(is_default=True),
                name='unique_default_address_per_user'
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.province}"

    @property
    def full_address(self):
        """Trả về chuỗi địa chỉ đầy đủ để hiển thị"""
        parts = [self.detail]
        if self.hamlet:
            parts.append(self.hamlet)
        parts.append(self.ward)
        parts.append(self.province)
        return ", ".join(parts)

    def save(self, *args, **kwargs):
        """Đảm bảo chỉ có 1 địa chỉ mặc định cho mỗi user"""
        if self.is_default:
            # Bỏ default của các địa chỉ cũ
            Address.objects.filter(
                user=self.user, 
                is_default=True
            ).exclude(
                address_id=self.address_id
            ).update(is_default=False)
        return super().save(*args, **kwargs)