from django.contrib.auth.models import AbstractUser
from django.db import models
import os

def user_avatar_upload_path(instance, filename):
    """
    Tạo đường dẫn upload cho avatar user
    Lưu vào: media/user/{user_id}/{filename}
    """
    # Lấy extension của file
    ext = filename.split('.')[-1]
    # Tạo tên file mới: avatar.{ext}
    filename = f'avatar.{ext}'
    # Return path: user/{user_id}/avatar.{ext}
    return os.path.join('user', str(instance.id), filename)

class User(AbstractUser):
    ROLE_CHOICES = [
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
        ('admin', 'Admin'),
    ]

    # Bỏ user_id vì AbstractUser đã có sẵn primary key id (AutoField)
    # Bỏ username, email, password vì AbstractUser có sẵn các trường đó
    # (có thể ghi đè nếu muốn thay đổi unique=True, max_length…)

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='buyer',
        verbose_name="Vai trò",
        help_text="Xác định quyền của người dùng: Buyer, Seller, Admin"
    )
    full_name = models.CharField(
        max_length=100,
        verbose_name="Họ và tên",
        help_text="Tên đầy đủ của người dùng"
    )
    phone = models.CharField(
        max_length=20,
        verbose_name="Số điện thoại",
        help_text="Số điện thoại liên hệ"
    )
    birth_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Ngày sinh",
        help_text="Ngày sinh của người dùng"
    )
    avatar = models.ImageField(
        upload_to=user_avatar_upload_path,
        null=True,
        blank=True,
        verbose_name="Ảnh đại diện",
        help_text="Ảnh đại diện của người dùng (lưu tại D:/PBL6/BackEnd/SHOEX/media/user/)"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Ngày tạo",
        help_text="Ngày giờ người dùng được tạo"
    )
    # AbstractUser đã có sẵn is_active, is_staff, is_superuser, last_login, date_joined

    def __str__(self):
        return self.username
    
    def get_avatar_url(self):
        """
        Trả về URL của avatar, hoặc default nếu không có
        """
        if self.avatar and self.avatar.url:
            return self.avatar.url
        return '/media/user/default-avatar.png'  # Default avatar path
