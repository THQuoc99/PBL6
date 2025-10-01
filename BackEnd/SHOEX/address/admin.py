from django.contrib import admin
from .models import Province, Ward, Hamlet, Address


@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ['province_id', 'name']
    search_fields = ['name']
    ordering = ['name']
    
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('province_id', 'name')
        }),
    )
    
    readonly_fields = ['province_id']


@admin.register(Ward)
class WardAdmin(admin.ModelAdmin):
    list_display = ['ward_id', 'name', 'province']
    list_filter = ['province']
    search_fields = ['name', 'province__name']
    autocomplete_fields = ['province']
    ordering = ['province__name', 'name']
    
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('ward_id', 'province', 'name')
        }),
    )
    
    readonly_fields = ['ward_id']


@admin.register(Hamlet)
class HamletAdmin(admin.ModelAdmin):
    list_display = ['hamlet_id', 'name', 'ward', 'province_name']
    list_filter = ['ward__province', 'ward']
    search_fields = ['name', 'ward__name', 'ward__province__name']
    autocomplete_fields = ['ward']
    ordering = ['ward__province__name', 'ward__name', 'name']
    
    def province_name(self, obj):
        return obj.ward.province.name
    province_name.short_description = 'Tỉnh/Thành phố'
    
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('hamlet_id', 'ward', 'name')
        }),
    )
    
    readonly_fields = ['hamlet_id']


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['address_id', 'user', 'province', 'ward', 'hamlet', 'is_default']
    list_filter = ['province', 'ward', 'is_default']
    search_fields = ['user__username', 'user__full_name', 'detail', 'province__name', 'ward__name']
    autocomplete_fields = ['user', 'province', 'ward', 'hamlet']
    readonly_fields = ['address_id', 'full_address']
    
    fieldsets = (
        ('Thông tin người dùng', {
            'fields': ('address_id', 'user')
        }),
        ('Địa chỉ', {
            'fields': ('province', 'ward', 'hamlet', 'detail', 'full_address')
        }),
        ('Trạng thái', {
            'fields': ('is_default',)
        }),
    )
    
    actions = ['set_as_default', 'unset_default']
    
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
    
    def save_model(self, request, obj, form, change):
        """Override để xử lý logic default address"""
        super().save_model(request, obj, form, change)
        
    def get_queryset(self, request):
        """Tối ưu hóa query"""
        return super().get_queryset(request).select_related(
            'user', 'province', 'ward', 'hamlet', 'ward__province'
        )
