from django.db import models
from django.conf import settings
from django.utils.text import slugify

class Store(models.Model):
    """
    Thông tin Cửa hàng (Seller)
    Map với bảng: store_store
    """
    store_id = models.CharField(
        primary_key=True, 
        max_length=50, 
        verbose_name="Mã cửa hàng",
        help_text="Mã định danh duy nhất (VD: SHOP-001)"
    )
    name = models.CharField(max_length=255, verbose_name="Tên cửa hàng")
    slug = models.SlugField(unique=True, max_length=255)
    description = models.TextField(verbose_name="Mô tả")
    
    # Thông tin liên hệ
    email = models.EmailField(max_length=255)
    phone = models.CharField(max_length=20)
    address = models.TextField(verbose_name="Địa chỉ hiển thị")
    
    # Hình ảnh
    avatar = models.ImageField(upload_to='store/avatars/', null=True, blank=True)
    cover_image = models.ImageField(upload_to='store/covers/', null=True, blank=True)
    
    # Chỉ số đánh giá
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=5.0)
    followers_count = models.IntegerField(default=0)
    products_count = models.IntegerField(default=0)
    
    # Trạng thái
    is_verified = models.BooleanField(default=False, verbose_name="Đã xác minh")
    is_active = models.BooleanField(default=True, verbose_name="Đang hoạt động")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-rating', '-created_at']
        verbose_name = "Cửa hàng"
        verbose_name_plural = "Cửa hàng"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class AddressStore(models.Model):
    """
    Địa chỉ lấy hàng của Shop
    Map với bảng: store_addressstore
    """
    address_id = models.AutoField(primary_key=True)
    store = models.ForeignKey(
        Store, 
        on_delete=models.CASCADE, 
        related_name='addresses'
    )
    province = models.CharField(max_length=100, verbose_name="Tỉnh/TP")
    ward = models.CharField(max_length=100, verbose_name="Phường/Xã")
    hamlet = models.CharField(max_length=100, null=True, blank=True, verbose_name="Thôn/Xóm")
    detail = models.CharField(max_length=255, verbose_name="Chi tiết")
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Địa chỉ kho hàng"
        constraints = [
            models.UniqueConstraint(
                fields=['store'], 
                condition=models.Q(is_default=True), 
                name='unique_default_address_per_store'
            )
        ]

    def __str__(self):
        return f"{self.store.name} - {self.province}"


class StoreImage(models.Model):
    """Thư viện ảnh của Shop"""
    store = models.ForeignKey(
        Store, 
        on_delete=models.CASCADE, 
        related_name='images'
    )
    image = models.ImageField(upload_to='store/gallery/')
    title = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


class StoreFollower(models.Model):
    """Người dùng theo dõi Shop"""
    store = models.ForeignKey(
        Store, 
        on_delete=models.CASCADE, 
        related_name='followers'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='followed_stores'
    )
    is_active = models.BooleanField(default=True)
    followed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['store', 'user']
        verbose_name = "Người theo dõi"