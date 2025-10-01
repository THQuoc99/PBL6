from django.contrib import admin
from .models import Review

# Register your models here.
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('review_id', 'order_item', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('order_item__id', 'comment')