from django.db import models
from django.core.exceptions import ValidationError
import json
from django.utils.text import slugify
# Create your models here.

class Category(models.Model):
    """Danh mục sản phẩm - Cây phân cấp"""
    category_id = models.AutoField(
        primary_key=True,
        verbose_name="Mã danh mục"
    )
    name = models.CharField(
        max_length=100,
        verbose_name="Tên danh mục"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Mô tả"
    )
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
        verbose_name="Ảnh đại diện danh mục",
        help_text="Ảnh thumbnail cho danh mục"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Hoạt động"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Ngày tạo"
    )

    class Meta:
        verbose_name = "Danh mục"
        verbose_name_plural = "Danh mục"
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    """Sản phẩm chính - Master data"""
    product_id = models.AutoField(
        primary_key=True,
        verbose_name="Mã sản phẩm"
    )
    slug = models.SlugField(unique=True, blank=True)
    seller = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name="Người bán"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name="Danh mục"
    )
    name = models.CharField(
        max_length=200,
        verbose_name="Tên sản phẩm"
    )
    description = models.TextField(
        verbose_name="Mô tả sản phẩm"
    )
    base_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        verbose_name="Giá cơ bản",
        help_text="Giá tham khảo, giá thực tế sẽ theo variant"
    )
    
    # Thông tin bổ sung
    brand = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Thương hiệu"
    )
    model_code = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Mã model",
        unique=True
    )
    
    # Metadata
    is_active = models.BooleanField(
        default=True,
        verbose_name="Hoạt động"
    )
    is_featured = models.BooleanField(
        default=False,  
        verbose_name="Sản phẩm nổi bật"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Ngày tạo"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Ngày cập nhật"
    )

    class Meta:
        verbose_name = "Sản phẩm"
        verbose_name_plural = "Sản phẩm" 
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['seller', 'is_active']),
            models.Index(fields=['category', 'is_active']),
        ]

    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.model_code:
            # Đếm xem hiện có bao nhiêu sản phẩm
            count = Product.objects.count() + 1
            # Gộp lại: prefix + số thứ tự (4 chữ số)
            self.model_code = f"PRD-{count:04d}"
        super().save(*args, **kwargs)
    @property
    def min_price(self):
        """Giá thấp nhất từ variants"""
        return self.variants.filter(is_active=True).aggregate(
            models.Min('price')
        )['price__min'] or self.base_price
    @property  
    def max_price(self):
        """Giá cao nhất từ variants"""
        return self.variants.filter(is_active=True).aggregate(
            models.Max('price')
        )['price__max'] or self.base_price

    @property
    def total_stock(self):
        """Tổng tồn kho"""
        return self.variants.filter(is_active=True).aggregate(
            models.Sum('stock')
        )['stock__sum'] or 0

    @property
    def available_colors(self):
        """Các màu có sẵn"""
        return self.color_images.filter(is_available=True)


class ProductAttribute(models.Model):
    """Định nghĩa các thuộc tính có thể có (Size, Color, Material, Style...)"""
    ATTRIBUTE_TYPE_CHOICES = [
        ('select', 'Lựa chọn từ danh sách'),
        ('color', 'Màu sắc (có ảnh)'),
        ('text', 'Nhập text'),
        ('number', 'Số'),
    ]
    
    attribute_id = models.AutoField(
        primary_key=True,
        verbose_name="Mã thuộc tính"
    )
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Tên thuộc tính",
        help_text="VD: Size, Color, Material, Style, Storage..."
    )
    type = models.CharField(
        max_length=10,
        choices=ATTRIBUTE_TYPE_CHOICES,
        verbose_name="Loại thuộc tính"
    )
    is_required = models.BooleanField(
        default=True,
        verbose_name="Bắt buộc"
    )
    has_image = models.BooleanField(
        default=False,
        verbose_name="Có ảnh riêng",
        help_text="Thuộc tính này có ảnh riêng không (thường là Color)"
    )
    display_order = models.IntegerField(
        default=0,
        verbose_name="Thứ tự hiển thị"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Ngày tạo"
    )

    class Meta:
        verbose_name = "Thuộc tính sản phẩm"
        verbose_name_plural = "Thuộc tính sản phẩm"
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name


class ProductAttributeOption(models.Model):
    """Các tùy chọn cụ thể cho từng thuộc tính của sản phẩm"""
    option_id = models.AutoField(
        primary_key=True,
        verbose_name="Mã tùy chọn"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='attribute_options',
        verbose_name="Sản phẩm"
    )
    attribute = models.ForeignKey(
        ProductAttribute,
        on_delete=models.CASCADE,
        related_name='product_options',
        verbose_name="Thuộc tính"
    )
    value = models.CharField(
        max_length=100,
        verbose_name="Giá trị",
        help_text="VD: 39, Đen, Da thật, High-top..."
    )
    value_code = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Mã giá trị",
        help_text="VD: #000000 cho màu đen, XL cho size..."
    )
    image = models.ImageField(
        upload_to='products/attributes/%Y/%m/',
        blank=True,
        null=True,
        verbose_name="Ảnh",
        help_text="Upload ảnh cho tùy chọn này (nếu attribute.has_image = True)"
    )
    display_order = models.IntegerField(
        default=0,
        verbose_name="Thứ tự hiển thị"
    )
    is_available = models.BooleanField(
        default=True,
        verbose_name="Còn hàng"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Ngày tạo"
    )

    class Meta:
        verbose_name = "Tùy chọn thuộc tính"
        verbose_name_plural = "Tùy chọn thuộc tính"
        ordering = ['attribute__display_order', 'display_order', 'value']
        constraints = [
            models.UniqueConstraint(
                fields=['product', 'attribute', 'value'],
                name='unique_product_attribute_value'
            ),
        ]

    def get_variants(self):
        """Lấy tất cả variants có tùy chọn này"""
        return self.product.variants.filter(
            option_combinations__contains=f'"{self.attribute.name}": "{self.value}"',
            is_active=True
        )

    def get_available_combinations(self, exclude_attributes=None):
        """Lấy các kết hợp khác có sẵn khi đã chọn tùy chọn này"""
        exclude_attributes = exclude_attributes or []
        variants = self.get_variants().filter(stock__gt=0)
        
        combinations = {}
        for variant in variants:
            try:
                options = json.loads(variant.option_combinations)
                for attr_name, attr_value in options.items():
                    if attr_name not in exclude_attributes and attr_name != self.attribute.name:
                        if attr_name not in combinations:
                            combinations[attr_name] = set()
                        combinations[attr_name].add(attr_value)
            except (json.JSONDecodeError, TypeError):
                pass
        
        # Convert sets to sorted lists
        for attr_name in combinations:
            combinations[attr_name] = sorted(list(combinations[attr_name]))
        
        return combinations

    @property
    def image_url(self):
        """Trả về URL của ảnh (backward compatibility)"""
        if self.image:
            return self.image.url
        return None
    
    def __str__(self):
        return f"{self.product.name} - {self.attribute.name}: {self.value}"


class ProductVariant(models.Model):
    """Biến thể sản phẩm - SKU thực tế (Size + Color + ...)"""
    variant_id = models.AutoField(
        primary_key=True,
        verbose_name="Mã biến thể"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='variants',
        verbose_name="Sản phẩm"
    )
    sku = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="SKU"
    )
    
    # Thông tin giá và kho
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Giá bán"
    )
    stock = models.IntegerField(
        default=0,
        verbose_name="Tồn kho"
    )
    
    # Thông tin vật lý
    weight = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0.1,
        verbose_name="Khối lượng (kg)"
    )
    
    # Kết hợp thuộc tính (JSON: {"Size": "39", "Color": "Đen"})
    option_combinations = models.JSONField(
        verbose_name="Kết hợp thuộc tính",
        help_text='JSON format: {"Size": "39", "Color": "Đen"}'
    )
    
    # Metadata
    is_active = models.BooleanField(
        default=True,
        verbose_name="Hoạt động"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Ngày tạo"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Ngày cập nhật"
    )

    class Meta:
        verbose_name = "Biến thể sản phẩm"
        verbose_name_plural = "Biến thể sản phẩm"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', 'is_active']),
            models.Index(fields=['sku']),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.sku}"

    @property
    def color_name(self):
        """Lấy tên màu từ option_combinations"""
        try:
            options = json.loads(self.option_combinations) if isinstance(self.option_combinations, str) else self.option_combinations
            return options.get('Color', 'N/A')
        except (json.JSONDecodeError, TypeError):
            return 'N/A'

    @property  
    def size_name(self):
        """Lấy size từ option_combinations"""
        try:
            options = json.loads(self.option_combinations) if isinstance(self.option_combinations, str) else self.option_combinations
            return options.get('Size', 'N/A')
        except (json.JSONDecodeError, TypeError):
            return 'N/A'

    @property
    def is_in_stock(self):
        """Kiểm tra còn hàng"""
        return self.stock > 0 and self.is_active

    @property
    def color_image(self):
        """Lấy ảnh màu tương ứng"""
        color = self.color_name
        if color != 'N/A':
            return self.product.color_images.filter(color_name=color).first()
        return None

    def clean(self):
        """Validate dữ liệu"""
        if self.price <= 0:
            raise ValidationError("Giá phải lớn hơn 0")
        
        if self.stock < 0:
            raise ValidationError("Tồn kho không được âm")
        
        # Validate JSON format
        try:
            if isinstance(self.option_combinations, str):
                json.loads(self.option_combinations)
        except json.JSONDecodeError:
            raise ValidationError("option_combinations phải là JSON hợp lệ")


class ProductImage(models.Model):
    """
    Bảng lưu trữ ảnh cho Product (ảnh đại diện + ảnh chính)
    Thiết kế đơn giản: 1 Product có 1 ảnh đại diện + nhiều ảnh chính
    """
    image_id = models.AutoField(
        primary_key=True,
        verbose_name="Mã ảnh",
        help_text="ID tự tăng, duy nhất cho mỗi ảnh"
    )
    
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='gallery_images',
        verbose_name="Sản phẩm",
        help_text="Sản phẩm chứa ảnh này"
    )
    
    image = models.ImageField(
        upload_to='products/gallery/%Y/%m/',
        verbose_name="Ảnh sản phẩm",
        help_text="Upload ảnh sản phẩm",
        null=True,  
        blank=True 
    )
    
    is_thumbnail = models.BooleanField(
        default=False,
        verbose_name="Ảnh đại diện",
        help_text="Đánh dấu ảnh đại diện của sản phẩm (chỉ được 1 ảnh)"
    )
    
    alt_text = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Alt text",
        help_text="Mô tả ảnh cho SEO"
    )
    
    display_order = models.IntegerField(
        default=0,
        verbose_name="Thứ tự hiển thị",
        help_text="Thứ tự hiển thị ảnh (ảnh đại diện luôn đầu tiên)"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Ngày tạo"
    )
    
    class Meta:
        ordering = ['-is_thumbnail', 'display_order', 'created_at']
        constraints = [
            # Đảm bảo mỗi product chỉ có 1 ảnh đại diện
            models.UniqueConstraint(
                fields=['product'],
                condition=models.Q(is_thumbnail=True),
                name='unique_product_thumbnail'
            ),
        ]
    
    @property
    def image_url(self):
        """Trả về URL của ảnh (backward compatibility)"""
        if self.image:
            return self.image.url
        return None
    
    def __str__(self):
        img_type = "Ảnh đại diện" if self.is_thumbnail else "Ảnh chính"
        return f"{img_type} - {self.product.name}"

