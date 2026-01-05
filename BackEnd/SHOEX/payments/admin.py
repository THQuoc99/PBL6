from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'payment_id',
        'order',
        'user',
        'store',
        'payment_method',
        'amount',
        'status',
        'transaction_id',
        'paid_at',
        'created_at',
    )
    list_filter = ('status', 'payment_method', 'paid_at', 'created_at')
    search_fields = ('transaction_id', 'order__order_id', 'user__username', 'user__email')
    ordering = ('-created_at',)
    autocomplete_fields = ['order', 'user', 'store']

    fieldsets = (
        ('Thông tin chính', {
            'fields': ('payment_id', 'order', 'user', 'store', 'payment_method', 'amount')
        }),
        ('Trạng thái & Giao dịch', {
            'fields': ('status', 'transaction_id', 'paid_at')
        }),
        ('Gateway', {
            'fields': ('gateway_response',)
        }),
        ('Hệ thống', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    readonly_fields = ('payment_id', 'created_at', 'updated_at', 'paid_at')