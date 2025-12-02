from django.contrib import admin
from .models import Store, AddressStore, StoreImage

class AddressStoreInline(admin.TabularInline):
    model = AddressStore
    extra = 0

class StoreImageInline(admin.TabularInline):
    model = StoreImage
    extra = 0

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ['store_id', 'name', 'phone', 'rating', 'is_verified', 'is_active']
    search_fields = ['name', 'store_id', 'email']
    list_filter = ['is_verified', 'is_active']
    inlines = [AddressStoreInline, StoreImageInline]