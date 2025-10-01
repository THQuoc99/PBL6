from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = ('payment_id', 'order', 'status', 'transaction_id', 'paid_at')
    
    # Fields to filter by in the sidebar
    list_filter = ('status', 'paid_at')
    
    # Fields to search for in the search bar
    search_fields = ('transaction_id', 'order__id')
    
    # Fields to group in the detail view
    fieldsets = (
        ('Thông tin thanh toán', {
            'fields': ('payment_id', 'order', 'status', 'transaction_id', 'paid_at')
        }),
        ('Chi tiết khác', {
            'fields': ('payment_method', 'amount'),
        }),
    )
    
    # Read-only fields
    readonly_fields = ('payment_id', 'paid_at')