from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from django.db.models import Q
from decimal import Decimal

from .models import Voucher, UserVoucher
from .serializers import VoucherSerializer, UserVoucherSerializer, ApplyVoucherSerializer

class VoucherViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API Voucher:
    - GET /api/discounts/ : Danh sách voucher đang hoạt động
    - POST /api/discounts/save/ : Lưu voucher vào ví
    - GET /api/discounts/my-wallet/ : Xem ví voucher của tôi
    - POST /api/discounts/check/ : Kiểm tra voucher có hợp lệ với đơn hàng không
    """
    serializer_class = VoucherSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['code', 'seller__name']

    def get_queryset(self):
        now = timezone.now().date()
        # Chỉ lấy voucher đang active và còn hạn
        return Voucher.objects.filter(
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        ).order_by('end_date')

    @action(detail=False, methods=['get'], url_path='store-vouchers')
    def store_vouchers(self, request):
        """Lọc voucher theo store_id"""
        store_id = request.query_params.get('store_id')
        if not store_id:
            return Response({'error': 'Thiếu store_id'}, status=400)
        
        vouchers = self.get_queryset().filter(type='store', seller_id=store_id)
        serializer = self.get_serializer(vouchers, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated], url_path='my-wallet')
    def my_wallet(self, request):
        """Lấy danh sách voucher user đã lưu"""
        user_vouchers = UserVoucher.objects.filter(user=request.user).select_related('voucher')
        serializer = UserVoucherSerializer(user_vouchers, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def save(self, request):
        """Lưu voucher vào ví"""
        code = request.data.get('code')
        if not code:
            return Response({'error': 'Vui lòng nhập mã voucher'}, status=400)
        
        try:
            voucher = Voucher.objects.get(code=code, is_active=True)
        except Voucher.DoesNotExist:
            return Response({'error': 'Voucher không tồn tại hoặc đã hết hạn'}, status=404)

        # Kiểm tra hạn
        now = timezone.now().date()
        if voucher.end_date < now:
            return Response({'error': 'Voucher đã hết hạn'}, status=400)

        # Kiểm tra giới hạn toàn hệ thống
        if voucher.usage_limit and voucher.usage_limit <= 0: # Logic đơn giản, thực tế cần count UserVoucher hoặc OrderVoucher
             return Response({'error': 'Voucher đã hết lượt sử dụng'}, status=400)

        # Lưu
        uv, created = UserVoucher.objects.get_or_create(user=request.user, voucher=voucher)
        if not created:
            return Response({'message': 'Bạn đã lưu voucher này rồi'}, status=200)
        
        return Response({'message': 'Lưu voucher thành công'}, status=201)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def check(self, request):
        """Kiểm tra điều kiện áp dụng voucher (cho bước Checkout)"""
        serializer = ApplyVoucherSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        
        code = serializer.validated_data['code']
        order_amount = serializer.validated_data['order_amount']
        store_id = serializer.validated_data.get('store_id')

        try:
            voucher = Voucher.objects.get(code=code, is_active=True)
        except Voucher.DoesNotExist:
            return Response({'valid': False, 'error': 'Mã không tồn tại'}, status=404)

        # 1. Check hạn sử dụng
        now = timezone.now().date()
        if not (voucher.start_date <= now <= voucher.end_date):
            return Response({'valid': False, 'error': 'Mã chưa bắt đầu hoặc đã hết hạn'}, status=400)

        # 2. Check đơn tối thiểu
        if order_amount < voucher.min_order_amount:
            return Response({
                'valid': False, 
                'error': f'Đơn hàng chưa đạt tối thiểu {voucher.min_order_amount:,.0f}đ'
            }, status=400)

        # 3. Check loại Voucher (Store vs Platform)
        if voucher.type == 'store':
            if not store_id or str(voucher.seller_id) != str(store_id):
                return Response({'valid': False, 'error': 'Voucher này không áp dụng cho shop hiện tại'}, status=400)

        # 4. Tính toán mức giảm
        discount_amount = Decimal(0)
        if voucher.discount_type == 'fixed':
            discount_amount = voucher.discount_value
        else: # percent
            discount_amount = order_amount * (voucher.discount_value / 100)
            if voucher.max_discount:
                discount_amount = min(discount_amount, voucher.max_discount)
        
        # Đảm bảo không giảm quá giá trị đơn
        discount_amount = min(discount_amount, order_amount)

        return Response({
            'valid': True,
            'voucher_id': voucher.voucher_id,
            'code': voucher.code,
            'discount_amount': discount_amount,
            'final_amount': order_amount - discount_amount
        })