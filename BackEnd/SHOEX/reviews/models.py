from django.db import models
from django.conf import settings

class Review(models.Model):
    SIZE_ACCURACY_CHOICES = [
        ('true_to_size', 'Đúng size'),
        ('runs_small', 'Hơi chật'),
        ('runs_large', 'Hơi rộng'),
    ]
    
    COLOR_ACCURACY_CHOICES = [
        ('accurate', 'Giống ảnh'),
        ('lighter', 'Nhạt hơn'),
        ('darker', 'Đậm hơn'),
    ]
    
    MATERIAL_QUALITY_CHOICES = [
        ('good', 'Tốt'),
        ('average', 'Bình thường'),
        ('bad', 'Kém'),
    ]

    review_id = models.AutoField(primary_key=True, verbose_name="Mã đánh giá")
    
    # Link 1-1 với OrderItem: Mỗi sản phẩm trong đơn chỉ được đánh giá 1 lần
    order_item = models.OneToOneField(
        'orders.OrderItem',
        on_delete=models.CASCADE,
        related_name='review',
        verbose_name="Sản phẩm mua"
    )
    
    rating = models.IntegerField(verbose_name="Xếp hạng", help_text="1-5 sao")
    
    # Các tiêu chí chi tiết
    size_accuracy = models.CharField(max_length=20, choices=SIZE_ACCURACY_CHOICES, null=True, blank=True)
    color_accuracy = models.CharField(max_length=20, choices=COLOR_ACCURACY_CHOICES, null=True, blank=True)
    material_quality = models.CharField(max_length=20, choices=MATERIAL_QUALITY_CHOICES, null=True, blank=True)
    
    comment = models.TextField(null=True, blank=True, verbose_name="Nội dung")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Đánh giá"

    def __str__(self):
        return f"Review #{self.review_id} ({self.rating}*) - {self.order_item.variant.sku}"


class ReviewImage(models.Model):
    """Ảnh đính kèm đánh giá"""
    image_id = models.AutoField(primary_key=True)
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='reviews/images/')
    caption = models.CharField(max_length=200, null=True, blank=True)
    display_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order']


class ReviewVideo(models.Model):
    """Video đính kèm đánh giá"""
    video_id = models.AutoField(primary_key=True)
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='videos')
    video = models.FileField(upload_to='reviews/videos/')
    thumbnail = models.ImageField(upload_to='reviews/videos/thumbnails/', null=True, blank=True)
    duration = models.CharField(max_length=10, null=True, blank=True) # VD: "0:30"
    caption = models.CharField(max_length=200, null=True, blank=True)
    display_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)


class ReviewHelpful(models.Model):
    """Người dùng vote hữu ích cho đánh giá"""
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='helpful_votes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_helpful = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Mỗi user chỉ vote 1 lần cho 1 review
        constraints = [
            models.UniqueConstraint(fields=['review', 'user'], name='unique_helpful_vote_per_review')
        ]