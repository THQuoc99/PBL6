from django.db import models

# Create your models here.

class Review(models.Model):
    review_id = models.AutoField(
        primary_key=True,
        verbose_name="Mã đánh giá",
        help_text="ID tự tăng, duy nhất cho mỗi đánh giá"
    )
    order_item = models.ForeignKey(
        'orders.OrderItem',
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name="Mục đơn hàng",
        help_text="Mục đơn hàng liên kết với đánh giá này"
    )
    rating = models.IntegerField(
        verbose_name="Xếp hạng",
        help_text="Xếp hạng của đánh giá (1-5)"
    )
    comment = models.TextField(
        blank=True,
        null=True,
        verbose_name="Bình luận",
        help_text="Bình luận chi tiết của đánh giá"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Ngày tạo",
        help_text="Ngày giờ đánh giá được tạo"
    )

    def __str__(self):
        return f"Review {self.review_id}"