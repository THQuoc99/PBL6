from django.contrib import admin
from .models import Brand
from django.utils.html import format_html

# Định nghĩa cách mô hình Brand sẽ được hiển thị trong Admin
class BrandAdmin(admin.ModelAdmin):
    # Các trường hiển thị trong danh sách (list view)
    list_display = ('brand_id', 'name', 'country', 'display_logo', 'is_active', 'created_at')
    
    # Các trường cho phép tìm kiếm
    search_fields = ('name', 'description', 'country')
    
    # Các trường cho phép lọc
    list_filter = ('is_active', 'country', 'created_at')
    
    # Các trường sẽ tự động tạo slug từ name
    prepopulated_fields = {'slug': ('name',)}
    
    # Chỉ đọc các trường này (người dùng không thể chỉnh sửa)
    readonly_fields = ('brand_id', 'created_at', 'updated_at', 'display_logo')
    
    # Tùy chỉnh hiển thị logo
    def display_logo(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="width: 50px; height: 50px;" />', obj.logo.url)
        return "No Logo"
    
    display_logo.short_description = "Logo"

# Đăng ký mô hình với tùy chỉnh Admin
admin.site.register(Brand, BrandAdmin)