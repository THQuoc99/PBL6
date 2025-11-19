from django.contrib import admin
from .models import Review

# Register your models here.
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('review_id', 'user', 'product', 'rating', 'created_at')
    list_filter = ('rating', 'size_accuracy', 'color_accuracy', 'material_quality', 'created_at')
    search_fields = ('order_item__order__buyer__username', 'order_item__variant__product__name', 'comment')
    readonly_fields = ('user', 'product', 'store', 'created_at')
    
    def user(self, obj):
        return obj.user
    user.short_description = "Người đánh giá"
    
    def product(self, obj):
        return obj.product
    product.short_description = "Sản phẩm"
    
    def store(self, obj):
        return obj.store
    store.short_description = "Cửa hàng"