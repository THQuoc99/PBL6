# brand/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Brand

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['id', 'logo_preview', 'name', 'country', 'is_active', 'created_at']
    search_fields = ['name', 'country']
    list_filter = ['is_active', 'country']
    
    # Tự động sinh slug từ tên thương hiệu khi nhập liệu
    prepopulated_fields = {'slug': ('name',)}
    
    # Hiển thị ảnh logo nhỏ trong danh sách
    def logo_preview(self, obj):
        if obj.logo:
            # Lưu ý: Nếu field logo của bạn là CharField (lưu URL/tên file) như trong SQL gốc
            # thì bạn hiển thị text. Nếu bạn đã đổi thành ImageField thì dùng obj.logo.url
            return obj.logo 
        return "-"
    logo_preview.short_description = "Logo"