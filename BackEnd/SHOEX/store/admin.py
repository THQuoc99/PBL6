from django.contrib import admin
from .models import (
    Store, StoreUser, StoreCategory, StoreReview, StoreFollower,
    StoreAnalytics, StoreSettings, StoreImage, StoreRole, 
    StorePermission, StoreInvitation
)


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('store_id', 'name', 'rating', 'total_reviews', 'followers_count', 'is_verified', 'status', 'created_at')
    list_filter = ('status', 'is_verified', 'is_active', 'created_at')
    search_fields = ('store_id', 'name', 'email', 'phone')
    readonly_fields = ('rating', 'total_reviews', 'followers_count', 'products_count', 'total_sales', 'total_revenue', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('store_id', 'name', 'slug', 'description')
        }),
        ('Liên hệ', {
            'fields': ('email', 'phone', 'address', 'location')
        }),
        ('Hình ảnh', {
            'fields': ('avatar', 'cover_image', 'logo')
        }),
        ('Thống kê', {
            'fields': ('rating', 'total_reviews', 'followers_count', 'products_count', 'total_sales', 'total_revenue')
        }),
        ('Trạng thái', {
            'fields': ('is_verified', 'is_active', 'status')
        }),
        ('Vận chuyển', {
            'fields': ('cod_enabled', 'express_shipping', 'standard_shipping', 'free_shipping_min')
        }),
        ('Chính sách', {
            'fields': ('return_policy', 'shipping_policy', 'warranty_policy')
        }),
        ('Hệ thống', {
            'fields': ('currency', 'timezone', 'join_date', 'created_at', 'updated_at')
        }),
    )


@admin.register(StoreUser)
class StoreUserAdmin(admin.ModelAdmin):
    list_display = ('store', 'user', 'role', 'status', 'joined_at', 'created_at')
    list_filter = ('role', 'status', 'created_at')
    search_fields = ('store__name', 'user__username', 'user__email')
    autocomplete_fields = ['store', 'user', 'invited_by']
    readonly_fields = ('created_at', 'updated_at')


@admin.register(StoreCategory)
class StoreCategoryAdmin(admin.ModelAdmin):
    list_display = ('store', 'category', 'is_primary', 'created_at')
    list_filter = ('is_primary', 'created_at')
    search_fields = ('store__name', 'category__name')
    autocomplete_fields = ['store', 'category']


@admin.register(StoreReview)
class StoreReviewAdmin(admin.ModelAdmin):
    list_display = ('store', 'user', 'rating', 'is_verified', 'helpful_count', 'created_at')
    list_filter = ('rating', 'is_verified', 'created_at')
    search_fields = ('store__name', 'user__username', 'title', 'comment')
    autocomplete_fields = ['store', 'user', 'order']
    readonly_fields = ('helpful_count', 'created_at', 'updated_at')


@admin.register(StoreFollower)
class StoreFollowerAdmin(admin.ModelAdmin):
    list_display = ('store', 'user', 'is_active', 'followed_at')
    list_filter = ('is_active', 'followed_at')
    search_fields = ('store__name', 'user__username')
    autocomplete_fields = ['store', 'user']


@admin.register(StoreAnalytics)
class StoreAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('store', 'date', 'views', 'visitors', 'orders', 'revenue', 'new_followers')
    list_filter = ('date',)
    search_fields = ('store__name',)
    autocomplete_fields = ['store']
    date_hierarchy = 'date'


@admin.register(StoreSettings)
class StoreSettingsAdmin(admin.ModelAdmin):
    list_display = ('store', 'auto_confirm_orders', 'notification_email', 'vacation_mode')
    list_filter = ('auto_confirm_orders', 'notification_email', 'vacation_mode')
    search_fields = ('store__name',)
    autocomplete_fields = ['store']


@admin.register(StoreImage)
class StoreImageAdmin(admin.ModelAdmin):
    list_display = ('store', 'image_type', 'title', 'is_active', 'sort_order', 'created_at')
    list_filter = ('image_type', 'is_active', 'created_at')
    search_fields = ('store__name', 'title')
    autocomplete_fields = ['store']
    ordering = ('store', 'sort_order')


@admin.register(StoreRole)
class StoreRoleAdmin(admin.ModelAdmin):
    list_display = ('role_name', 'role_display_name', 'is_system_role', 'created_at')
    list_filter = ('is_system_role', 'created_at')
    search_fields = ('role_name', 'role_display_name')
    readonly_fields = ('created_at',)


@admin.register(StorePermission)
class StorePermissionAdmin(admin.ModelAdmin):
    list_display = ('permission_name', 'display_name', 'permission_group', 'is_active', 'created_at')
    list_filter = ('permission_group', 'is_active', 'created_at')
    search_fields = ('permission_name', 'display_name')
    readonly_fields = ('created_at',)


@admin.register(StoreInvitation)
class StoreInvitationAdmin(admin.ModelAdmin):
    list_display = ('store', 'email', 'role', 'status', 'invited_by', 'invited_at', 'expires_at')
    list_filter = ('role', 'status', 'invited_at', 'expires_at')
    search_fields = ('store__name', 'email', 'invited_by__username')
    autocomplete_fields = ['store', 'invited_by']
    readonly_fields = ('invitation_token', 'invited_at', 'created_at')
