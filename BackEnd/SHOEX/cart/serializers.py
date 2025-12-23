from rest_framework import serializers
from .models import Cart, CartItem
from products.models import ProductImage

class CartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source='variant.product.product_id', read_only=True)
    product_name = serializers.CharField(source='variant.product.name', read_only=True)
    brand = serializers.CharField(source='variant.product.brand', read_only=True)
    price = serializers.DecimalField(source='variant.price', max_digits=12, decimal_places=2, read_only=True)
    attributes = serializers.JSONField(source='variant.option_combinations', read_only=True)
    image = serializers.SerializerMethodField()
    sub_total = serializers.SerializerMethodField()
    
    # Thêm thông tin store để tính phí ship riêng
    store_id = serializers.CharField(source='variant.product.store.store_id', read_only=True)
    store_name = serializers.CharField(source='variant.product.store.name', read_only=True)
    
    # Địa chỉ kho hàng của store (lấy default address)
    store_address = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['item_id', 'variant', 'product_id', 'product_name', 'brand', 'attributes', 
                  'quantity', 'price', 'image', 'sub_total', 'store_id', 'store_name', 'store_address']
    
    def get_store_address(self, obj):
        """Lấy địa chỉ kho mặc định của store"""
        try:
            from django.conf import settings
            store = obj.variant.product.store
            default_addr = store.addresses.filter(is_default=True).first()
            
            if default_addr:
                # GHTK cần: province (tỉnh), district (quận/huyện), ward (phường/xã)
                # AddressStore fields: province, hamlet (quận/huyện), ward (phường/xã)
                
                district = default_addr.hamlet  # hamlet = quận/huyện
                
                # Validate district - nếu là số hoặc "Khu phố" thì dùng warehouse mặc định
                if not district or district.strip().isdigit() or 'khu phố' in district.lower():
                    # Fallback to default warehouse
                    print(f"⚠️ Invalid district '{district}' for store {store.store_id}, using default warehouse")
                    warehouse = settings.WAREHOUSE_ADDRESS
                    return {
                        'province': warehouse['province'],
                        'district': warehouse['district'],
                        'ward': warehouse.get('ward', ''),
                        'detail': warehouse.get('detail', '')
                    }
                
                return {
                    'province': default_addr.province,
                    'district': district,  # hamlet = district
                    'ward': default_addr.ward,
                    'detail': default_addr.detail
                }
            
            # No address found, use default warehouse
            warehouse = settings.WAREHOUSE_ADDRESS
            return {
                'province': warehouse['province'],
                'district': warehouse['district'],
                'ward': warehouse.get('ward', ''),
                'detail': warehouse.get('detail', '')
            }
        except Exception as e:
            print(f"❌ Error getting store address: {e}")
            return None

    def get_image(self, obj):
        try:
            product = obj.variant.product
            thumbnail = product.gallery_images.filter(is_thumbnail=True).first()
            if thumbnail: return thumbnail.image.url
            first_img = product.gallery_images.first()
            if first_img: return first_img.image.url
            return None
        except:
            return None

    def get_sub_total(self, obj):
        return obj.variant.price * obj.quantity

class CartSerializer(serializers.ModelSerializer):
    # ✅ SỬA LỖI: Bỏ source='items' vì tên field đã là 'items' rồi
    items = CartItemSerializer(many=True, read_only=True) 
    
    total_amount = serializers.SerializerMethodField()
    total_items = serializers.IntegerField(read_only=True) # property count items

    class Meta:
        model = Cart
        fields = ['cart_id', 'total_amount', 'total_items', 'items']

    def get_total_amount(self, obj):
        return obj.total_amount