from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from django.db.models import Q
from decimal import Decimal
import os

from .models import Voucher, UserVoucher, VoucherReservation, VoucherUsage, OrderVoucher
from django.utils import timezone as dj_timezone
from datetime import timedelta
from .serializers import VoucherSerializer, UserVoucherSerializer, ApplyVoucherSerializer
from django.db.models import Count, Sum
from django.db import transaction

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

        # 3. Check loại Voucher (Store / Platform / Shipping)
        if voucher.type == 'store':
            if not store_id or str(voucher.seller_id) != str(store_id):
                return Response({'valid': False, 'error': 'Voucher này không áp dụng cho shop hiện tại'}, status=400)
        if voucher.type == 'shipping':
            # shipping vouchers should be validated against shipping_fee (not order_amount)
            target = serializer.validated_data.get('target', 'order')
            shipping_fee = serializer.validated_data.get('shipping_fee')
            if target != 'shipping':
                return Response({'valid': False, 'error': 'Voucher giao hàng phải kiểm tra với target=shipping'}, status=400)
            if shipping_fee is None:
                return Response({'valid': False, 'error': 'Thiếu shipping_fee để kiểm tra voucher giao hàng'}, status=400)

        # 3.b Check per-user limit (count existing uses + reservations)
        try:
            used_count = 0
            # Prefer VoucherUsage if exists
            vu = VoucherUsage.objects.filter(user=request.user, voucher=voucher).first()
            if vu:
                used_count = vu.used_count
            else:
                used_count = OrderVoucher.objects.filter(order__buyer=request.user, voucher=voucher).count()

            # Include active reservations by this user
            reserved = VoucherReservation.objects.filter(user=request.user, voucher=voucher).count()
            used_count += reserved

            if voucher.per_user_limit and used_count >= voucher.per_user_limit:
                return Response({'valid': False, 'error': 'Bạn đã sử dụng voucher này quá giới hạn'}, status=400)
        except Exception:
            pass

        # 4. Tính toán mức giảm
        discount_amount = Decimal(0)
        # If shipping voucher, compute on shipping_fee
        if voucher.type == 'shipping':
            shipping_fee = serializer.validated_data.get('shipping_fee')
            if voucher.is_free_shipping:
                discount_amount = Decimal(shipping_fee)
            else:
                if voucher.discount_type == 'fixed':
                    discount_amount = voucher.discount_value
                else:
                    discount_amount = Decimal(shipping_fee) * (voucher.discount_value / 100)
                    if voucher.max_discount:
                        discount_amount = min(discount_amount, voucher.max_discount)
            discount_amount = min(discount_amount, Decimal(shipping_fee))
        else:
            if voucher.discount_type == 'fixed':
                discount_amount = voucher.discount_value
            else: # percent
                # default to order_amount if provided
                amt = serializer.validated_data.get('order_amount') or Decimal(0)
                discount_amount = amt * (voucher.discount_value / 100)
                if voucher.max_discount:
                    discount_amount = min(discount_amount, voucher.max_discount)
            # Đảm bảo không giảm quá giá trị đơn
            amt = serializer.validated_data.get('order_amount') or Decimal(0)
            discount_amount = min(discount_amount, amt)
        # Xây dựng thông tin applicability để frontend dễ hiển thị
        applicable_stores = []
        applies_to_products = []
        applies_to_categories = []

        # Nếu voucher specific cho cửa hàng
        if voucher.type == 'store' and voucher.seller_id:
            applicable_stores = [voucher.seller_id]

        # Nếu voucher có danh sách store áp dụng (platform voucher scoped)
        if hasattr(voucher, 'voucher_stores'):
            stores = voucher.voucher_stores.all()
            if stores.exists():
                applicable_stores = [s.store_id if hasattr(s, 'store_id') else s.store.pk for s in stores]

        # Sản phẩm/danh mục áp dụng
        if hasattr(voucher, 'voucher_products'):
            applies_to_products = [vp.product_id if hasattr(vp, 'product_id') else vp.product.pk for vp in voucher.voucher_products.all()]

        if hasattr(voucher, 'voucher_categories'):
            applies_to_categories = [vc.category_id if hasattr(vc, 'category_id') else vc.category.pk for vc in voucher.voucher_categories.all()]

        return Response({
            'valid': True,
            'voucher_id': voucher.voucher_id,
            'code': voucher.code,
            'type': voucher.type,
            'is_free_shipping': getattr(voucher, 'is_free_shipping', False),
            'discount_amount': discount_amount,
            'final_amount': order_amount - discount_amount,
            'min_order_amount': voucher.min_order_amount,
            'per_user_limit': voucher.per_user_limit,
            'applicable_stores': applicable_stores,
            'applies_to_products': applies_to_products,
            'applies_to_categories': applies_to_categories,
        })

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated], url_path='report')
    def report(self, request):
        """Simple admin report: totals and per-voucher summary.

        Requires staff user.
        """
        if not request.user.is_staff:
            return Response({'error': 'Chỉ admin mới được truy cập'}, status=403)

        total_reservations = VoucherReservation.objects.count()
        total_used = 0
        total_discount = 0
        top_vouchers = []

        from .models import OrderVoucher
        agg = OrderVoucher.objects.aggregate(total_uses=Count('id'), total_discount=Sum('discount_amount'))
        total_used = agg.get('total_uses') or 0
        total_discount = float(agg.get('total_discount') or 0)

        qs = OrderVoucher.objects.values('voucher__voucher_id', 'voucher__code', 'voucher__seller_id').annotate(
            uses=Count('id'), total_discount=Sum('discount_amount')
        ).order_by('-uses')[:50]

        for row in qs:
            top_vouchers.append({
                'voucher_id': row['voucher__voucher_id'],
                'code': row['voucher__code'],
                'seller_id': row.get('voucher__seller_id'),
                'uses': row['uses'],
                'total_discount': float(row['total_discount'] or 0)
            })

        return Response({
            'total_reservations': total_reservations,
            'total_voucher_uses': total_used,
            'total_discount_amount': total_discount,
            'top_vouchers': top_vouchers,
        })

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def reserve(self, request):
        """Reserve a voucher for the current user for a short period.

        Body: { "code": "VOUCHER", "seconds": 300 }
        """
        code = request.data.get('code')
        seconds = int(request.data.get('seconds', 300))
        if not code:
            return Response({'error': 'Thiếu code'}, status=400)

        try:
            with transaction.atomic():
                v = Voucher.objects.select_for_update().get(code=code, is_active=True)
                now = dj_timezone.now()
                if not (v.start_date <= now.date() <= v.end_date):
                    return Response({'error': 'Voucher không hợp lệ (hết hạn)'}, status=400)

                if v.usage_limit and v.usage_limit <= 0:
                    return Response({'error': 'Voucher đã hết lượt sử dụng'}, status=400)

                # decrement usage_limit as reservation
                if v.usage_limit:
                    v.usage_limit = int(v.usage_limit) - 1
                    v.save()

                expires_at = now + timedelta(seconds=seconds)
                res = VoucherReservation.objects.create(voucher=v, user=request.user, expires_at=expires_at)
                # Log reservation
                try:
                    logs_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs.txt')
                    with open(logs_path, 'a', encoding='utf-8') as lf:
                        lf.write(f"{dj_timezone.now().isoformat()} RESERVE voucher={v.code} user={request.user.id} reservation_id={res.reservation_id}\n")
                except Exception as _:
                    pass

                return Response({'reservation_id': res.reservation_id, 'expires_at': expires_at}, status=201)
        except Voucher.DoesNotExist:
            return Response({'error': 'Voucher không tồn tại'}, status=404)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def release(self, request):
        """Release a reservation and restore voucher usage_limit.

        Body: { "reservation_id": 123 }
        """
        rid = request.data.get('reservation_id')
        if not rid:
            return Response({'error': 'Thiếu reservation_id'}, status=400)

        try:
            with transaction.atomic():
                res = VoucherReservation.objects.select_for_update().get(reservation_id=rid, user=request.user)
                v = res.voucher
                # restore usage_limit
                if v.usage_limit is None:
                    # unlimited -> nothing to restore
                    pass
                else:
                    v.usage_limit = int(v.usage_limit) + 1
                    v.save()

                res.delete()
                # Log release
                try:
                    logs_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs.txt')
                    with open(logs_path, 'a', encoding='utf-8') as lf:
                        lf.write(f"{dj_timezone.now().isoformat()} RELEASE voucher={v.code} user={request.user.id} reservation_id={rid}\n")
                except Exception:
                    pass

                return Response({'released': True}, status=200)
        except VoucherReservation.DoesNotExist:
            return Response({'error': 'Reservation không tồn tại'}, status=404)