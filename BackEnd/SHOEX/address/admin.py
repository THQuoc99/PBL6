from django.contrib import admin
from .models import Address

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['address_id', 'user', 'full_address_display', 'is_default']
    list_filter = ['province', 'is_default'] # Lọc theo tỉnh/thành (lưu dạng text)
    search_fields = ['user__username', 'user__full_name', 'detail', 'province', 'ward', 'hamlet']
    autocomplete_fields = ['user']
    readonly_fields = ['address_id']
    
    fieldsets = (
        ('Thông tin người dùng', {
            'fields': ('address_id', 'user')
        }),
        ('Địa chỉ', {
            # Các trường text mới
            'fields': ('province', 'ward', 'hamlet', 'detail')
        }),
        ('Trạng thái', {
            'fields': ('is_default',)
        }),
    )
    
    actions = ['set_as_default', 'unset_default']

    def full_address_display(self, obj):
        return obj.full_address
    full_address_display.short_description = "Địa chỉ đầy đủ"
    
    def set_as_default(self, request, queryset):
        """Action để đặt làm địa chỉ mặc định"""
        count = 0
        for address in queryset:
            address.set_as_default()
            count += 1
        self.message_user(request, f"Đã đặt {count} địa chỉ làm mặc định.")
    set_as_default.short_description = "Đặt làm địa chỉ mặc định"
    
    def unset_default(self, request, queryset):
        """Action để bỏ địa chỉ mặc định"""
        updated = queryset.update(is_default=False)
        self.message_user(request, f"Đã bỏ mặc định cho {updated} địa chỉ.")
    unset_default.short_description = "Bỏ địa chỉ mặc định"
    
    def get_queryset(self, request):
        """Tối ưu hóa query"""
        return super().get_queryset(request).select_related('user')