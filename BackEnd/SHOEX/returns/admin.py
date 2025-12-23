from django.contrib import admin
from .models import ReturnRequest, ReturnItem, ReturnImage, ReturnTracking


class ReturnItemInline(admin.TabularInline):
    model = ReturnItem
    extra = 0
    fields = ['order_item', 'quantity']


class ReturnImageInline(admin.TabularInline):
    model = ReturnImage
    extra = 0
    fields = ['image', 'uploaded_at']
    readonly_fields = ['uploaded_at']


class ReturnTrackingInline(admin.TabularInline):
    model = ReturnTracking
    extra = 0
    fields = ['status', 'note', 'created_by', 'created_at']
    readonly_fields = ['created_at']


@admin.register(ReturnRequest)
class ReturnRequestAdmin(admin.ModelAdmin):
    list_display = ['return_id', 'order', 'buyer', 'return_type', 'reason', 'status', 'created_at']
    list_filter = ['status', 'return_type', 'reason', 'created_at']
    search_fields = ['return_id', 'order__order_id', 'buyer__email', 'description']
    readonly_fields = ['created_at', 'updated_at', 'approved_at', 'completed_at']
    
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('order', 'sub_order', 'buyer', 'return_type', 'reason', 'description')
        }),
        ('Tài chính', {
            'fields': ('refund_amount',)
        }),
        ('Trạng thái', {
            'fields': ('status', 'return_tracking_code')
        }),
        ('Phản hồi', {
            'fields': ('shop_response', 'reject_reason')
        }),
        ('Thời gian', {
            'fields': ('created_at', 'updated_at', 'approved_at', 'completed_at')
        }),
    )
    
    inlines = [ReturnItemInline, ReturnImageInline, ReturnTrackingInline]
    
    actions = ['approve_returns', 'reject_returns']
    
    def approve_returns(self, request, queryset):
        updated = queryset.filter(status='pending').update(status='approved')
        self.message_user(request, f'Đã duyệt {updated} yêu cầu trả hàng')
    approve_returns.short_description = 'Duyệt yêu cầu đã chọn'
    
    def reject_returns(self, request, queryset):
        updated = queryset.filter(status='pending').update(status='rejected')
        self.message_user(request, f'Đã từ chối {updated} yêu cầu trả hàng')
    reject_returns.short_description = 'Từ chối yêu cầu đã chọn'
