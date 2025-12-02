from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # --- 1. Cấu hình danh sách hiển thị (List View) ---
    list_display = (
        "id", "username", "email", "role",
        "full_name", "phone", "avatar_preview", # Thêm xem trước ảnh
        "created_at", "is_active", "is_staff"
    )
    list_filter = ("role", "is_active", "is_staff", "created_at")
    search_fields = ("username", "email", "full_name", "phone")
    ordering = ("-created_at",)

    # --- 2. Cấu hình Form sửa User (Edit View) ---
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Thông tin cá nhân", {
            "fields": (
                "full_name", "email", "phone", 
                "role", "birth_date", "avatar"  # ✅ Đã thêm Avatar và Ngày sinh
            )
        }),
        ("Phân quyền", {
            "fields": (
                "is_active", "is_staff", "is_superuser", 
                "groups", "user_permissions"
            )
        }),
        ("Thời gian", {
            "fields": ("last_login", "date_joined", "created_at") # ✅ Thêm created_at để xem
        }),
    )
    
    # ✅ Quan trọng: created_at không sửa được nên phải set readonly
    readonly_fields = ["created_at", "last_login", "date_joined"]

    # --- 3. Cấu hình Form tạo User mới (Add View) ---
    # Lưu ý: Mặc định Django xử lý password, không cần khai báo password1/2 ở đây nếu không có CustomForm
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "username",
                "email", # Có thể nhập email ngay lúc tạo
                "role",  # Có thể chọn vai trò ngay lúc tạo
                "is_staff",
                "is_active"
            ),
        }),
    )

    # Hàm hiển thị ảnh nhỏ (Thumbnail)
    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" style="width: 35px; height: 35px; object-fit: cover; border-radius: 50%; border: 1px solid #ddd;" />', 
                obj.avatar.url
            )
        return "-"
    avatar_preview.short_description = "Avatar"