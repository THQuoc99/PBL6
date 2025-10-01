from django.contrib import admin
from .models import Shipment

# Register your models here.
@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('shipment_id', 'status', 'pick_name', 'name', 'pick_date', 'value', 'created_at')
    list_filter = ('status', 'pick_date', 'is_freeship')
    search_fields = ('shipment_id', 'tracking_code', 'pick_name', 'name', 'tel')
    ordering = ('-created_at',)