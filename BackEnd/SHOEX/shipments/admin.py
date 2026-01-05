from django.contrib import admin
from django.utils.html import format_html

from .models import Shipment, ShipmentTracking


# =========================
# Inline Tracking (xem log ngay trong Shipment)
# =========================
class ShipmentTrackingInline(admin.TabularInline):
    model = ShipmentTracking
    extra = 0
    can_delete = False

    readonly_fields = (
        'carrier_status',
        'carrier_status_text',
        'message',
        'event_time',
        'synced_at',
    )

    fields = (
        'carrier_status',
        'carrier_status_text',
        'event_time',
        'message',
    )

    ordering = ('-event_time',)


# =========================
# Shipment Admin
# =========================
@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):

    list_display = (
        'shipment_id',
        'sub_order',
        'store',
        'user',
        'tracking_code',
        'status',
        'pick_money',
        'value',
        'total_weight',
        'created_at',
        'updated_at',
        'ghtk_tracking_link',
    )

    search_fields = (
        'tracking_code',
        'sub_order__sub_order_id',
        'store__name',
        'user__email',
        'user__username',
    )

    list_filter = (
        'status',
        'store',
        'transport',
        'created_at',
    )

    ordering = ('-created_at',)

    readonly_fields = (
        'tracking_code',
        'created_at',
        'updated_at',
    )

    inlines = [ShipmentTrackingInline]

    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': (
                ('user', 'store'),
                ('sub_order',),
                ('tracking_code', 'status'),
            )
        }),
        ('Giá trị & vận chuyển', {
            'fields': (
                ('pick_money', 'value', 'total_weight'),
                ('transport',),
                ('note',),
            )
        }),
        ('Thời gian', {
            'fields': (
                'created_at',
                'updated_at',
            )
        }),
    )

    actions = [
        'mark_as_shipping',
        'mark_as_out_for_delivery',
        'mark_as_completed',
        'mark_as_cancelled',
    ]

    # ===== ADMIN ACTIONS =====
    def mark_as_shipping(self, request, queryset):
        updated = queryset.update(status='shipping')
        self.message_user(
            request,
            f"Đã cập nhật {updated} vận đơn sang trạng thái 'Vận chuyển'."
        )
    mark_as_shipping.short_description = "Chuyển sang 'Vận chuyển'"

    def mark_as_out_for_delivery(self, request, queryset):
        updated = queryset.update(status='out_for_delivery')
        self.message_user(
            request,
            f"Đã cập nhật {updated} vận đơn sang trạng thái 'Chờ giao hàng'."
        )
    mark_as_out_for_delivery.short_description = "Chuyển sang 'Chờ giao hàng'"

    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(
            request,
            f"Đã cập nhật {updated} vận đơn sang trạng thái 'Hoàn thành'."
        )
    mark_as_completed.short_description = "Chuyển sang 'Hoàn thành'"

    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(
            request,
            f"Đã cập nhật {updated} vận đơn sang trạng thái 'Đã hủy'."
        )
    mark_as_cancelled.short_description = "Chuyển sang 'Đã hủy'"

    # ===== LINK TRA CỨU GHTK =====
    def ghtk_tracking_link(self, obj):
        if not obj.tracking_code:
            return "-"
        url = f"https://i.ghtk.vn/{obj.tracking_code}"
        return format_html(
            '<a href="{}" target="_blank">Tra cứu</a>',
            url
        )
    ghtk_tracking_link.short_description = "Tra cứu GHTK"


# =========================
# ShipmentTracking Admin (LOG – READ ONLY)
# =========================
@admin.register(ShipmentTracking)
class ShipmentTrackingAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'shipment',
        'label_id',
        'partner_id',
        'carrier_status',
        'carrier_status_text',
        'event_time',
        'synced_at',
    )

    search_fields = (
        'label_id',
        'partner_id',
        'shipment__tracking_code',
    )

    list_filter = (
        'carrier_status',
        'event_time',
    )

    ordering = ('-event_time',)

    readonly_fields = (
        'shipment',
        'label_id',
        'partner_id',
        'carrier_status',
        'carrier_status_text',
        'message',
        'event_time',
        'synced_at',
        'estimated_pick_time',
        'estimated_deliver_time',
        'raw_response',
    )

    fieldsets = (
        ('Thông tin vận đơn', {
            'fields': (
                'shipment',
                'label_id',
                'partner_id',
            )
        }),
        ('Trạng thái từ GHTK', {
            'fields': (
                'carrier_status',
                'carrier_status_text',
                'message',
            )
        }),
        ('Thời gian', {
            'fields': (
                'event_time',
                'synced_at',
            )
        }),
        ('Dự kiến', {
            'fields': (
                'estimated_pick_time',
                'estimated_deliver_time',
            )
        }),
        ('Raw API response', {
            'fields': ('raw_response',),
        }),
    )
