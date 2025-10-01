from django.contrib.auth.models import AbstractUser
from django.db import models

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
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Ngày tạo",
        help_text="Ngày giờ người dùng được tạo"
    )
    # AbstractUser đã có sẵn is_active, is_staff, is_superuser, last_login, date_joined

    def __str__(self):
        return self.username
