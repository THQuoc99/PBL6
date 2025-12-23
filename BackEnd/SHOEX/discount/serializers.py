from rest_framework import serializers
from .models import Voucher, UserVoucher, VoucherProduct, VoucherStore
from store.models import Store
from django.utils import timezone

class VoucherSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source='seller.name', read_only=True)
    is_saved = serializers.SerializerMethodField()
    
    class Meta:
        model = Voucher
        fields = [
            'voucher_id', 'code', 'type', 'store_name', 'seller',
            'discount_type', 'discount_value', 
            'min_order_amount', 'max_discount',
            'is_free_shipping',
            'start_date', 'end_date', 
            'usage_limit', 'is_saved'
        ]

    def get_is_saved(self, obj):
        """Kiểm tra user hiện tại đã lưu voucher này chưa"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return UserVoucher.objects.filter(user=request.user, voucher=obj).exists()
        return False

class UserVoucherSerializer(serializers.ModelSerializer):
    """Serializer hiển thị voucher trong ví của user"""
    voucher = VoucherSerializer(read_only=True)
    
    class Meta:
        model = UserVoucher
        fields = ['id', 'voucher', 'saved_at', 'used_count', 'can_use']

class ApplyVoucherSerializer(serializers.Serializer):
    """Serializer để validate input khi check voucher"""
    code = serializers.CharField(required=True)
    order_amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    store_id = serializers.CharField(required=False, allow_null=True) # Nếu mua hàng của shop cụ thể
    # target: 'order' or 'shipping' - dùng để cho biết kiểm tra trên tổng hàng hay trên phí vận chuyển
    target = serializers.ChoiceField(choices=[('order', 'Order'), ('shipping', 'Shipping')], required=False, default='order')
    shipping_fee = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)