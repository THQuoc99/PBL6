from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
        ('admin', 'Admin'),
    ]

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='buyer', # Nên có default để tránh lỗi khi tạo user bằng lệnh createsuperuser
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
        unique=True,
        verbose_name="Số điện thoại",
        help_text="Số điện thoại liên hệ"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Ngày tạo",
        help_text="Ngày giờ người dùng được tạo"
    )
    
    # --- CÁC TRƯỜNG MỚI TRONG DATANEW.SQL ---
    
    # Khớp với avatar character varying(100)
    avatar = models.ImageField(
        upload_to='users/avatars/', 
        max_length=100, 
        null=True, 
        blank=True,
        verbose_name="Ảnh đại diện"
    )
    
    # Khớp với birth_date date
    birth_date = models.DateField(
        null=True, 
        blank=True,
        verbose_name="Ngày sinh"
    )

    def __str__(self):
        return self.username
