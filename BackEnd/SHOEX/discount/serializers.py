from rest_framework import serializers
from .models import Voucher, UserVoucher, VoucherUsage

class VoucherSerializer(serializers.ModelSerializer):
    # Map store -> store_id để frontend dễ dùng
    store_id = serializers.SerializerMethodField()
    store_name = serializers.SerializerMethodField()
    
    # Giữ lại field 'type' để tương thích với Frontend cũ (nếu có)
    # Frontend của bạn đang dùng v.type -> map nó vào v.scope
    type = serializers.CharField(source='scope', read_only=True)

    class Meta:
        model = Voucher
        fields = [
            'voucher_id', 
            'code', 
            'scope',        # Tên mới
            'type',         # Tên cũ (alias)
            'store',        # Object store (dùng để write nếu cần)
            'store_id',     # ID store (dùng để read)
            'store_name',   # Tên store
            'discount_type', 
            'discount_value', 
            'min_order_amount', 
            'max_discount', 
            'start_date', 
            'end_date', 
            'usage_limit', 
            'per_user_limit', 
            'is_free_shipping', 
            'payment_method_required', # Trường mới thêm
            'is_active'
        ]
        extra_kwargs = {
            'store': {'write_only': True} # Khi read dùng store_id/store_name cho gọn
        }

    def get_store_id(self, obj):
        if obj.store:
            return obj.store.store_id # Hoặc obj.store.pk tùy model Store của bạn
        return None

    def get_store_name(self, obj):
        if obj.store:
            return obj.store.name
        return None

class UserVoucherSerializer(serializers.ModelSerializer):
    voucher = VoucherSerializer(read_only=True)
    
    class Meta:
        model = UserVoucher
        fields = ['id', 'user', 'voucher', 'saved_at', 'used_count']

class ApplyVoucherSerializer(serializers.Serializer):
    code = serializers.CharField()
    order_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    store_id = serializers.CharField(required=False, allow_null=True)
    shipping_fee = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    payment_method = serializers.CharField(required=False, default='COD') # Thêm field này để check điều kiện thanh toán