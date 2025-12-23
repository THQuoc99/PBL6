from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from decimal import Decimal
from django.db import transaction
import datetime

from .models import Voucher, UserVoucher, VoucherReservation, VoucherUsage
from .serializers import VoucherSerializer, UserVoucherSerializer, ApplyVoucherSerializer

class VoucherViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = VoucherSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        now = timezone.now()
        return Voucher.objects.filter(
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        ).order_by('end_date')

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated], url_path='my-wallet')
    def my_wallet(self, request):
        """Lấy danh sách voucher user đã lưu"""
        user_vouchers = UserVoucher.objects.filter(user=request.user).select_related('voucher')
        serializer = UserVoucherSerializer(user_vouchers, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def available(self, request):
        """
        API Lấy danh sách voucher khả dụng cho giỏ hàng
        """
        # 1. Nhận dữ liệu đầu vào
        # Chuyển tất cả store_id về string để so sánh an toàn
        store_ids = [str(x) for x in request.data.get('store_ids', [])]
        total_amount = Decimal(str(request.data.get('total_amount', 0)))
        
        print(f"--- DEBUG AVAILABLE VOUCHERS ---")
        print(f"User: {request.user.email}")
        print(f"Input Store IDs: {store_ids}")
        print(f"Input Total Amount: {total_amount}")

        now = timezone.now()

        # 2. Lấy tất cả voucher đang active (Khoan hãy check ngày để debug xem có voucher không)
        all_vouchers = Voucher.objects.filter(is_active=True)
        print(f"Total Active Vouchers found: {all_vouchers.count()}")

        response_data = {
            "store_vouchers": [],
            "platform_vouchers": [],
            "shipping_vouchers": []
        }

        # Lấy danh sách voucher user đã lưu (để đánh dấu is_saved)
        saved_voucher_ids = UserVoucher.objects.filter(user=request.user).values_list('voucher_id', flat=True)

        for v in all_vouchers:
            # --- START FILTER LOGIC ---
            reason = None
            is_usable = True

            # 2.1 Check ngày (Debug: in ra nếu sai ngày)
            if not (v.start_date <= now <= v.end_date):
                # Tạm thời vẫn hiện voucher hết hạn nhưng đánh dấu không dùng được (hoặc ẩn luôn tùy logic)
                # Ở đây ta ẩn luôn để danh sách gọn, nhưng print ra để biết
                print(f"Skipping {v.code}: Date invalid ({v.start_date} - {v.end_date} vs {now})")
                continue

            # 2.2 Check số lượng tổng (Usage Limit)
            if v.usage_limit is not None and v.usage_limit <= 0:
                is_usable = False
                reason = "Đã hết lượt sử dụng"

            # 2.3 Check số lượng cá nhân (User Limit)
            # Check trong bảng Usage lịch sử
            vu = VoucherUsage.objects.filter(user=request.user, voucher=v).first()
            used_count = vu.used_count if vu else 0
            
            # Check cả trong ví (UserVoucher) cho chắc
            uv = UserVoucher.objects.filter(user=request.user, voucher=v).first()
            wallet_used = uv.used_count if uv else 0
            
            final_used = max(used_count, wallet_used)

            if final_used >= v.per_user_limit:
                is_usable = False
                reason = "Bạn đã dùng hết lượt"

            # 2.4 Check đơn tối thiểu
            # Lưu ý: Với voucher Store, total_amount ở đây là tổng đơn, 
            # đúng ra phải so với subtotal của store. Nhưng ở API list này ta cứ cho qua,
            # bước chọn (check) chi tiết sẽ validate lại.
            if total_amount < v.min_order_amount:
                is_usable = False
                reason = f"Đơn tối thiểu {v.min_order_amount:,.0f}đ"

            # --- SERIALIZE DATA ---
            v_data = VoucherSerializer(v).data
            v_data['is_saved'] = v.voucher_id in saved_voucher_ids
            v_data['is_usable'] = is_usable
            v_data['reason'] = reason

            # --- PHÂN LOẠI VÀO DANH SÁCH ---
            if v.scope == 'store':
                # Check xem voucher này thuộc store nào
                # Model voucher của bạn có trường 'store' (FK). 
                # Cần so sánh store.pk hoặc store.store_id với list store_ids gửi lên.
                
                # Lấy ID của store từ voucher (ép về string)
                voucher_store_id = str(v.store.pk) if v.store else ""
                
                # Nếu model Store của bạn có trường store_id riêng (VD: UUID), hãy dùng nó:
                # voucher_store_id = str(v.store.store_id) if v.store and hasattr(v.store, 'store_id') else str(v.store.pk)

                if voucher_store_id in store_ids:
                    response_data['store_vouchers'].append(v_data)
                else:
                    # Debug: Tại sao không khớp store
                    # print(f"Skipping Store Voucher {v.code}: Voucher Store {voucher_store_id} not in Cart Stores {store_ids}")
                    pass
            
            elif v.scope == 'platform':
                response_data['platform_vouchers'].append(v_data)
            
            elif v.scope == 'shipping':
                response_data['shipping_vouchers'].append(v_data)

        print(f"Returning: {len(response_data['store_vouchers'])} store, {len(response_data['platform_vouchers'])} platform, {len(response_data['shipping_vouchers'])} shipping")
        return Response(response_data)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def check(self, request):
        """
        Kiểm tra 1 voucher cụ thể (khi user chọn hoặc nhập code)
        """
        code = request.data.get('code')
        order_amount = Decimal(str(request.data.get('order_amount', 0)))
        store_id = str(request.data.get('store_id', ''))
        shipping_fee = Decimal(str(request.data.get('shipping_fee', 0)))
        payment_method = request.data.get('payment_method', 'COD')

        try:
            voucher = Voucher.objects.get(code=code, is_active=True)
        except Voucher.DoesNotExist:
            return Response({'valid': False, 'error': 'Voucher không tồn tại'}, status=404)

        # 1. Check hạn sử dụng
        now = timezone.now()
        if not (voucher.start_date <= now <= voucher.end_date):
            return Response({'valid': False, 'error': 'Voucher chưa bắt đầu hoặc đã hết hạn'}, status=400)

        # 2. Check số lượng toàn sàn
        if voucher.usage_limit is not None and voucher.usage_limit <= 0:
            return Response({'valid': False, 'error': 'Voucher đã hết lượt sử dụng'}, status=400)

        # 3. Check giới hạn người dùng
        # Check Usage History
        vu = VoucherUsage.objects.filter(user=request.user, voucher=voucher).first()
        used_count = vu.used_count if vu else 0
        
        # Cộng thêm đang giữ chỗ (reservation)
        reserved = VoucherReservation.objects.filter(user=request.user, voucher=voucher).count()
        
        if (used_count + reserved) >= voucher.per_user_limit:
            return Response({'valid': False, 'error': 'Bạn đã hết lượt dùng voucher này'}, status=400)

        # 4. Check Scope & Store
        if voucher.scope == 'store':
            if not store_id:
                return Response({'valid': False, 'error': 'Voucher shop cần thông tin cửa hàng'}, status=400)
            
            # So sánh ID (string)
            voucher_store_id = str(voucher.store.pk) if voucher.store else ""
            if voucher_store_id != store_id:
                return Response({'valid': False, 'error': 'Voucher không áp dụng cho shop hiện tại'}, status=400)
        
        # 5. Check Payment Method
        if voucher.payment_method_required != 'all':
            if voucher.payment_method_required != payment_method:
                return Response({
                    'valid': False, 
                    'error': f'Voucher chỉ áp dụng cho thanh toán qua {voucher.get_payment_method_required_display()}'
                }, status=400)

        # 6. Check Min Order & Tính giảm giá
        discount_amount = Decimal(0)
        
        if voucher.scope == 'shipping':
            # Check điều kiện đơn hàng tối thiểu
            if order_amount < voucher.min_order_amount:
                 return Response({'valid': False, 'error': f'Chưa đạt tối thiểu {voucher.min_order_amount:,.0f}đ'}, status=400)
            
            # --- [LOGIC MỚI] Ưu tiên tính giá trị giảm cụ thể trước ---
            
            # 1. Tính giá trị giảm (Fixed hoặc Percent)
            if voucher.discount_type == 'fixed':
                discount_amount = voucher.discount_value
            else: # Percent
                discount_amount = shipping_fee * (voucher.discount_value / 100)
            
            # Cap max discount (nếu có)
            if voucher.max_discount and discount_amount > voucher.max_discount:
                discount_amount = voucher.max_discount
            
            # 2. Xử lý trường hợp Freeship Extra (100%)
            # Nếu admin không điền value (tính ra 0) NHƯNG bật cờ is_free_shipping -> Thì mới giảm 100%
            if discount_amount == 0 and voucher.is_free_shipping:
                discount_amount = shipping_fee
            
            # 3. Không giảm quá phí ship thực tế (VD: ship 30k, mã giảm 50k -> chỉ giảm 30k)
            discount_amount = min(discount_amount, shipping_fee)

        else: # Store hoặc Platform
            # ... (Giữ nguyên logic cũ của Store/Platform)
            if order_amount < voucher.min_order_amount:
                 return Response({'valid': False, 'error': f'Chưa đạt tối thiểu {voucher.min_order_amount:,.0f}đ'}, status=400)

            base_amount = order_amount
            if voucher.discount_type == 'fixed':
                discount_amount = voucher.discount_value
            else:
                discount_amount = base_amount * (voucher.discount_value / 100)

            if voucher.max_discount and discount_amount > voucher.max_discount:
                discount_amount = voucher.max_discount

            discount_amount = min(discount_amount, base_amount)

        return Response({
            'valid': True,
            'voucher_id': voucher.voucher_id,
            'code': voucher.code,
            'scope': voucher.scope,
            'discount_amount': discount_amount,
            'min_order_amount': voucher.min_order_amount
        })

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def save(self, request):
        """Lưu voucher vào ví"""
        code = request.data.get('code')
        try:
            voucher = Voucher.objects.get(code=code, is_active=True)
            UserVoucher.objects.get_or_create(user=request.user, voucher=voucher)
            return Response({'message': 'Đã lưu voucher'})
        except Voucher.DoesNotExist:
            return Response({'error': 'Voucher không tồn tại'}, status=404)