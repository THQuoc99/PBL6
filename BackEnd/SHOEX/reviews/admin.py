from django.contrib import admin
from .models import Review, ReviewImage, ReviewVideo, ReviewHelpful

class ReviewImageInline(admin.TabularInline):
    model = ReviewImage
    extra = 1

class ReviewVideoInline(admin.TabularInline):
    model = ReviewVideo
    extra = 0

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('review_id', 'get_product', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    inlines = [ReviewImageInline, ReviewVideoInline]
    
    def get_product(self, obj):
        return obj.order_item.variant.product.name
    get_product.short_description = 'Sản phẩm'

@admin.register(ReviewHelpful)
class ReviewHelpfulAdmin(admin.ModelAdmin):
    list_display = ('review', 'user', 'created_at')