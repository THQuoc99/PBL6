from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Các cột hiển thị ở danh sách user
    list_display = (
        "id", "username", "email", "role",
        "full_name", "phone", "created_at",
        "is_active", "is_staff"
    )
    list_filter = ("role", "is_active", "is_staff", "created_at")
    search_fields = ("username", "email", "full_name", "phone")
    ordering = ("-created_at",)

    # Các field trong form xem/sửa user
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Thông tin cá nhân", {"fields": ("full_name", "email", "phone", "role")}),
        ("Phân quyền", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Thời gian", {"fields": ("last_login", "date_joined")}),  # ⚡ Bỏ created_at ở đây
    )

    # Các field trong form tạo user mới
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "username", "email", "full_name", "phone", "role",
                "password1", "password2",   # ⚡ Mặc định Django sẽ dùng form xác nhận password
                "is_active", "is_staff", "is_superuser"
            ),
        }),
    )
