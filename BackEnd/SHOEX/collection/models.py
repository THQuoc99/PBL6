from django.db import models
from django.utils.text import slugify


class Collection(models.Model):
    """Bộ sưu tập sản phẩm"""
    
    SEASON_CHOICES = [
        ('spring', 'Mùa xuân'),
        ('summer', 'Mùa hè'),
        ('autumn', 'Mùa thu'),
        ('winter', 'Mùa đông'),
        ('all_year', 'Thường niên'),
        ('special', 'Đặc biệt'),
    ]
    
    collection_id = models.CharField(
        max_length=50,
        primary_key=True,
        verbose_name="Mã bộ sưu tập",
        help_text="ID duy nhất cho bộ sưu tập (VD: summer-2024, sport-elite)"
    )
    
    name = models.CharField(
        max_length=255,
        verbose_name="Tên bộ sưu tập",
        help_text="VD: Summer Collection 2024, Sport Elite Series"
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Mô tả",
        help_text="Mô tả chi tiết về bộ sưu tập"
    )
    
    image = models.ImageField(
        upload_to='collections/images/',
        blank=True,
        null=True,
        verbose_name="Ảnh đại diện",
        help_text="Ảnh đại diện cho bộ sưu tập"
    )
    
    # Tự động tính từ số lượng product thuộc collection này
    product_count = models.IntegerField(
        default=0,
        verbose_name="Số sản phẩm",
        help_text="Số lượng sản phẩm trong bộ sưu tập (tự động tính)"
    )
    
    featured = models.BooleanField(
        default=False,
        verbose_name="Bộ sưu tập nổi bật",
        help_text="Hiển thị trong phần bộ sưu tập nổi bật"
    )
    
    season = models.CharField(
        max_length=20,
        choices=SEASON_CHOICES,
        default='all_year',
        verbose_name="Mùa",
        help_text="Mùa hoặc thời gian của bộ sưu tập"
    )
    
    season_custom = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Mùa tùy chỉnh",
        help_text="VD: Hè 2024, Thu Đông 2024 (nếu không dùng choices)"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Hoạt động",
        help_text="Bộ sưu tập có được hiển thị hay không"
    )
    
    display_order = models.IntegerField(
        default=0,
        verbose_name="Thứ tự hiển thị",
        help_text="Số càng nhỏ hiển thị càng trước"
    )
    
    # SEO
    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        verbose_name="Slug",
        help_text="URL thân thiện (tự động tạo từ tên)"
    )
    
    meta_title = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Meta title",
        help_text="Tiêu đề SEO"
    )
    
    meta_description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Meta description",
        help_text="Mô tả SEO"
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Ngày tạo"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Ngày cập nhật"
    )

    class Meta:
        verbose_name = "Bộ sưu tập"
        verbose_name_plural = "Bộ sưu tập"
        ordering = ['display_order', '-featured', '-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def update_product_count(self):
        """Cập nhật số lượng sản phẩm trong bộ sưu tập"""
        self.product_count = self.products.filter(is_active=True).count()
        self.save(update_fields=['product_count'])
    
    @property
    def season_display(self):
        """Hiển thị mùa (ưu tiên custom trước)"""
        return self.season_custom or self.get_season_display()


class ProductCollection(models.Model):
    """Liên kết sản phẩm với bộ sưu tập"""
    
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='product_collections',
        verbose_name="Sản phẩm"
    )
    
    collection = models.ForeignKey(
        Collection,
        on_delete=models.CASCADE,
        related_name='collection_products',
        verbose_name="Bộ sưu tập"
    )
    
    is_featured_in_collection = models.BooleanField(
        default=False,
        verbose_name="Nổi bật trong bộ sưu tập",
        help_text="Sản phẩm có nổi bật trong bộ sưu tập này không"
    )
    
    added_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Ngày thêm vào bộ sưu tập"
    )

    class Meta:
        verbose_name = "Sản phẩm trong bộ sưu tập"
        verbose_name_plural = "Sản phẩm trong bộ sưu tập"
        unique_together = ('product', 'collection')

    def __str__(self):
        return f"{self.product.name} - {self.collection.name}"
