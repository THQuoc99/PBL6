from django.contrib import admin

from .models import Settlement, SettlementItem, Refund


@admin.register(Settlement)
class SettlementAdmin(admin.ModelAdmin):
	list_display = (
		"settlement_id",
		"store",
		"total_amount",
		"status",
		"paid_at",
		"created_at",
	)
	list_filter = ("status", "created_at", "paid_at")
	search_fields = ("settlement_id", "store__name", "store__store_id")
	date_hierarchy = "created_at"


@admin.register(SettlementItem)
class SettlementItemAdmin(admin.ModelAdmin):
	list_display = (
		"settlement_item_id",
		"settlement",
		"sub_order",
		"amount",
		"created_at",
	)
	list_filter = ("created_at",)
	search_fields = (
		"settlement__settlement_id",
		"sub_order__sub_order_id",
	)


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
	list_display = (
		"refund_id",
		"sub_order",
		"settlement_item",
		"amount",
		"status",
		"created_at",
	)
	list_filter = ("status", "created_at")
	search_fields = (
		"refund_id",
		"sub_order__sub_order_id",
	)
