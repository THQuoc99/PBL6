from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

class Review(models.Model):
    ACCURACY_CHOICES = [
        ('smaller', 'Nhỏ hơn mô tả'),
        ('accurate', 'Đúng mô tả'),
        ('larger', 'Lớn hơn mô tả'),
    ]
    
    QUALITY_CHOICES = [
        ('poor', 'Kém'),
        ('average', 'Trung bình'),
        ('good', 'Tốt'),
        ('excellent', 'Xuất sắc'),
    ]

    review_id = models.AutoField(
        primary_key=True,
        verbose_name="Mã đánh giá",
        help_text="ID tự tăng, duy nhất cho mỗi đánh giá"
    )
    
    # Liên kết với đơn hàng để xác thực người mua đã mua sản phẩm
    order_item = models.ForeignKey(
        'orders.OrderItem',
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name="Mục đơn hàng",
        help_text="Mục đơn hàng liên kết với đánh giá này"
    )
    
    # Rating chung
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Xếp hạng tổng thể",
        help_text="Xếp hạng tổng thể của đánh giá (1-5 sao)"
    )
    
    # Đánh giá độ chính xác mô tả
    size_accuracy = models.CharField(
        max_length=20,
        choices=ACCURACY_CHOICES,
        null=True,
        blank=True,
        verbose_name="Độ chính xác size",
        help_text="Đánh giá về size so với mô tả"
    )
    
    color_accuracy = models.CharField(
        max_length=20,
        choices=ACCURACY_CHOICES,
        null=True,
        blank=True,
        verbose_name="Độ chính xác màu sắc",
        help_text="Đánh giá về màu sắc so với mô tả"
    )
    
    material_quality = models.CharField(
        max_length=20,
        choices=QUALITY_CHOICES,
        null=True,
        blank=True,
        verbose_name="Chất lượng chất liệu",
        help_text="Đánh giá chất lượng chất liệu"
    )
    
    # Bình luận chính
    comment = models.TextField(
        blank=True,
        null=True,
        verbose_name="Bình luận",
        help_text="Bình luận chi tiết của đánh giá"
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Ngày tạo",
        help_text="Ngày giờ đánh giá được tạo"
    )

    class Meta:
        verbose_name = "Đánh giá"
        verbose_name_plural = "Đánh giá"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_item']),
            models.Index(fields=['rating']),
            models.Index(fields=['created_at']),
        ]
        constraints = [
            # Đảm bảo một người chỉ đánh giá một lần cho mỗi order_item
            models.UniqueConstraint(
                fields=['order_item'],
                name='unique_review_per_order_item'
            ),
        ]

    def __str__(self):
        return f"Review {self.review_id} - {self.rating}⭐"
    
    @property
    def reviewer_name(self):
        """Trả về tên người đánh giá (có thể ẩn một phần để bảo mật)"""
        reviewer = self.order_item.order.buyer
        if hasattr(reviewer, 'full_name') and reviewer.full_name:
            name = reviewer.full_name
            if len(name) > 3:
                return f"{name[:2]}***{name[-1:]}"
            return f"{name[0]}***"
        elif hasattr(reviewer, 'username'):
            name = reviewer.username
            if len(name) > 3:
                return f"{name[:2]}***{name[-1:]}"
            return f"{name[0]}***"
        return "Người dùng ẩn danh"
    
    @property
    def rating_stars(self):
        """Trả về chuỗi sao cho rating"""
        return "⭐" * self.rating + "☆" * (5 - self.rating)
    
    @property
    def short_comment(self):
        """Trả về comment rút gọn (150 ký tự đầu)"""
        if self.comment:
            if len(self.comment) > 150:
                return f"{self.comment[:150]}..."
            return self.comment
        return "Không có bình luận"
    
    @property
    def variant_display(self):
        """Hiển thị thông tin phân loại đã mua từ order_item"""
        variant = self.order_item.variant
        try:
            import json
            if isinstance(variant.option_combinations, str):
                options = json.loads(variant.option_combinations)
            else:
                options = variant.option_combinations
            parts = []
            for key, value in options.items():
                parts.append(f"{key}: {value}")
            return ", ".join(parts)
        except:
            return f"SKU: {variant.sku}"


class ReviewImage(models.Model):
    """Bảng lưu trữ ảnh đính kèm trong review"""
    
    image_id = models.AutoField(
        primary_key=True,
        verbose_name="Mã ảnh"
    )
    
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name="Đánh giá",
        help_text="Đánh giá chứa ảnh này"
    )
    
    image = models.ImageField(
        upload_to='reviews/images/%Y/%m/',
        verbose_name="Ảnh đánh giá",
        help_text="Ảnh đính kèm trong đánh giá"
    )
    
    caption = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Mô tả ảnh",
        help_text="Mô tả ngắn cho ảnh"
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
        verbose_name = "Ảnh đánh giá"
        verbose_name_plural = "Ảnh đánh giá"
        ordering = ['display_order', 'created_at']
    
    def __str__(self):
        return f"Ảnh {self.image_id} - Review {self.review.review_id}"
    
    @property
    def image_url(self):
        """Trả về URL của ảnh"""
        if self.image:
            return self.image.url
        return None


class ReviewVideo(models.Model):
    """Bảng lưu trữ video đính kèm trong review"""
    
    video_id = models.AutoField(
        primary_key=True,
        verbose_name="Mã video"
    )
    
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='videos',
        verbose_name="Đánh giá",
        help_text="Đánh giá chứa video này"
    )
    
    video = models.FileField(
        upload_to='reviews/videos/%Y/%m/',
        verbose_name="Video đánh giá",
        help_text="Video đính kèm trong đánh giá"
    )
    
    thumbnail = models.ImageField(
        upload_to='reviews/video_thumbnails/%Y/%m/',
        null=True,
        blank=True,
        verbose_name="Ảnh thumbnail",
        help_text="Ảnh thumbnail cho video"
    )
    
    duration = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        verbose_name="Thời lượng",
        help_text="Thời lượng video (ví dụ: 0:04)"
    )
    
    caption = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Mô tả video",
        help_text="Mô tả ngắn cho video"
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
        verbose_name = "Video đánh giá"
        verbose_name_plural = "Video đánh giá"
        ordering = ['display_order', 'created_at']
    
    def __str__(self):
        return f"Video {self.video_id} - Review {self.review.review_id}"
    
    @property
    def video_url(self):
        """Trả về URL của video"""
        if self.video:
            return self.video.url
        return None


class ReviewHelpful(models.Model):
    """Bảng lưu trữ thông tin người dùng đánh giá review hữu ích"""
    
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='helpful_votes',
        verbose_name="Đánh giá"
    )
    
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='review_helpful_votes',
        verbose_name="Người dùng"
    )
    
    is_helpful = models.BooleanField(
        default=True,
        verbose_name="Hữu ích",
        help_text="True = hữu ích, False = không hữu ích"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Ngày vote"
    )
    
    class Meta:
        verbose_name = "Vote review hữu ích"
        verbose_name_plural = "Vote review hữu ích"
        constraints = [
            # Đảm bảo một user chỉ vote một lần cho mỗi review
            models.UniqueConstraint(
                fields=['review', 'user'],
                name='unique_helpful_vote_per_review'
            ),
        ]
    
    def __str__(self):
        status = "Hữu ích" if self.is_helpful else "Không hữu ích"
        return f"{self.user.username} - Review {self.review.review_id} - {status}"