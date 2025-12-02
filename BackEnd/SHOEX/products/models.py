from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils.text import slugify
import json

class Category(models.Model):
    """
    Danh mục sản phẩm
    Map với bảng: products_category
    """
    category_id = models.AutoField(primary_key=True, verbose_name="Mã danh mục")
    name = models.CharField(max_length=100, verbose_name="Tên danh mục")
    description = models.TextField(blank=True, null=True, verbose_name="Mô tả")
    
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategories',
        verbose_name="Danh mục cha"
    )
    
    thumbnail_image = models.ImageField(
        upload_to='categories/thumbnails/',
        blank=True,
        null=True,
        verbose_name="Ảnh đại diện"
    )
    
    is_active = models.BooleanField(default=True, verbose_name="Hoạt động")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        db_table = 'products_category'

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Sản phẩm chính
    Map với bảng: products_product
    """
    product_id = models.AutoField(primary_key=True, verbose_name="Mã sản phẩm")
    slug = models.SlugField(unique=True, max_length=50, blank=True) # DB set limit 50, code cũ 255
    
    # Map với store_id (varchar 50)
    store = models.ForeignKey(
        'store.Store',
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name="Cửa hàng",
        to_field='store_id',
        db_column='store_id'
    )
    
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name="Danh mục",
        db_column='category_id'
    )
    
    name = models.CharField(max_length=200, verbose_name="Tên sản phẩm")
    description = models.TextField(verbose_name="Mô tả sản phẩm")
    base_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Giá cơ bản")
    
    # --- QUAN HỆ VỚI BẢNG BRAND MỚI ---
    brand = models.ForeignKey(
        'brand.Brand',  # Đảm bảo đã tạo app 'brand'
        on_delete=models.SET_NULL,
        blank=True, 
        null=True, 
        related_name='products',
        verbose_name="Thương hiệu",
        db_column='brand_id'
    )
    # ----------------------------------

    model_code = models.CharField(max_length=100, blank=True, null=True, unique=True, verbose_name="Mã model")
    
    size_guide_image = models.CharField(max_length=100, blank=True, null=True) # DB lưu varchar
    
    rating = models.FloatField(default=0.0, verbose_name="Đánh giá trung bình")
    review_count = models.IntegerField(default=0, verbose_name="Số lượng đánh giá")

    is_active = models.BooleanField(default=True, verbose_name="Hoạt động")
    is_featured = models.BooleanField(default=False, verbose_name="Sản phẩm nổi bật")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        db_table = 'products_product'
        indexes = [
            models.Index(fields=['store', 'is_active']),
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['brand']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:50] # Cắt ngắn để vừa limit DB
        if not self.model_code:
            count = Product.objects.count() + 1
            self.model_code = f"PRD-{count:04d}"
        super().save(*args, **kwargs)


class ProductAttribute(models.Model):
    """
    Định nghĩa thuộc tính (Size, Color...)
    Map với bảng: products_productattribute
    """
    ATTRIBUTE_TYPE_CHOICES = [
        ('select', 'Lựa chọn'),
        ('color', 'Màu sắc'),
        ('text', 'Văn bản'),
        ('number', 'Số'),
    ]
    
    attribute_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    type = models.CharField(max_length=10, choices=ATTRIBUTE_TYPE_CHOICES)
    is_required = models.BooleanField(default=True)
    has_image = models.BooleanField(default=False)
    display_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order', 'name']
        db_table = 'products_productattribute'

    def __str__(self):
        return self.name


class ProductAttributeOption(models.Model):
    """
    Tùy chọn thuộc tính (Đỏ, Xanh, 39, 40...)
    Map với bảng: products_productattributeoption
    """
    option_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='attribute_options', db_column='product_id')
    attribute = models.ForeignKey(ProductAttribute, on_delete=models.CASCADE, related_name='product_options', db_column='attribute_id')
    
    value = models.CharField(max_length=100)
    value_code = models.CharField(max_length=50, blank=True, null=True) 
    
    image = models.CharField(max_length=100, blank=True, null=True) # DB lưu varchar
    
    display_order = models.IntegerField(default=0)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['attribute__display_order', 'display_order', 'value']
        db_table = 'products_productattributeoption'
        constraints = [
            models.UniqueConstraint(fields=['product', 'attribute', 'value'], name='unique_product_attribute_value')
        ]

    def __str__(self):
        return f"{self.product.name} - {self.value}"


class ProductVariant(models.Model):
    """
    Biến thể sản phẩm (SKU)
    Map với bảng: products_productvariant
    """
    variant_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants', db_column='product_id')
    
    sku = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    stock = models.IntegerField(default=0)
    weight = models.DecimalField(max_digits=8, decimal_places=2, default=0.1)
    
    # JSONB field
    option_combinations = models.JSONField(help_text='JSON format: {"Size": "39", "Color": "Đen"}')
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        db_table = 'products_productvariant'
        indexes = [
            models.Index(fields=['sku']),
        ]

    def __str__(self):
        return f"{self.sku}"


class ProductImage(models.Model):
    """
    Ảnh sản phẩm
    Map với bảng: products_productimage
    """
    image_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_images', db_column='product_id')
    
    # DB lưu đường dẫn ảnh (varchar 100). Dùng ImageField trong Django vẫn ổn vì nó map ra varchar
    image = models.ImageField(upload_to='products/gallery/', max_length=100)
    
    is_thumbnail = models.BooleanField(default=False)
    alt_text = models.CharField(max_length=200, blank=True, null=True)
    display_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_thumbnail', 'display_order']
        db_table = 'products_productimage'
        constraints = [
            models.UniqueConstraint(
                fields=['product'],
                condition=Q(is_thumbnail=True),
                name='unique_product_thumbnail'
            )
        ]