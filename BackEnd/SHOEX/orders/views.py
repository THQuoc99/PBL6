from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.utils.decorators import method_decorator
from decimal import Decimal
import os
import json

# Import Models
from .models import Order, SubOrder, OrderItem
from .serializers import OrderSerializer
from cart.models import Cart
from products.models import ProductVariant
from address.models import Address
from discount.models import Voucher, OrderVoucher, UserVoucher, VoucherReservation, VoucherUsage

# Import notification helpers
from notifications.utils import notify_order_created, notify_order_status_update

# Helper tính giảm giá
def calculate_voucher_discount(amount, voucher):
    """Tính số tiền giảm dựa trên loại voucher (fixed/percent) và max_discount"""
    discount = Decimal('0')
    if voucher.discount_type == 'fixed':
        discount = Decimal(voucher.discount_value)
    else:
        discount = (amount * Decimal(voucher.discount_value)) / Decimal('100')
        if voucher.max_discount:
            discount = min(discount, Decimal(voucher.max_discount))
    
    # Không giảm quá số tiền gốc
    return min(discount, amount)

@method_decorator(csrf_exempt, name='dispatch')
class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        # Lấy danh sách đơn hàng của user hiện tại, sắp xếp mới nhất
        return Order.objects.filter(buyer=self.request.user).order_by('-created_at')

    @action(detail=False, methods=['post'])
    def create_order(self, request):
        # 1. Lấy dữ liệu từ Request
        address_id = request.data.get('address_id')
        payment_method = request.data.get('payment_method', 'COD')
        
        # Validate Payment Method
        valid_methods = ['COD', 'VNPAY', 'PAYPAL']
        if payment_method not in valid_methods:
             return Response({'error': 'Phương thức thanh toán không hợp lệ'}, status=400)

        # TODO: Thực tế nên tính phí ship từ Backend (GHTK/GHN API) để bảo mật.
        # Ở đây tạm thời tin tưởng frontend gửi lên nhưng cần validate kỹ.
        shipping_fee_req = Decimal(str(request.data.get('shipping_fee', 0)))
        
        notes = request.data.get('notes', '')
        user = request.user

        # Nhận map vouchers: {"store_id": "CODE", "platform": "CODE", "shipping": "CODE"}
        vouchers_map = request.data.get('vouchers', {})
        if isinstance(vouchers_map, str):
            try:
                vouchers_map = json.loads(vouchers_map)
            except:
                vouchers_map = {}

        # Validate cơ bản
        if not address_id:
            return Response({'error': 'Vui lòng chọn địa chỉ giao hàng'}, status=400)
        
        # 2. Kiểm tra Địa chỉ
        try:
            address = Address.objects.get(address_id=address_id, user=user)
        except Address.DoesNotExist:
            return Response({'error': 'Địa chỉ không hợp lệ hoặc không tồn tại'}, status=400)

        # 3. Kiểm tra Giỏ hàng
        try:
            cart = Cart.objects.get(user=user)
            # Load trước các quan hệ để tối ưu query
            cart_items = cart.items.select_related(
                'variant', 
                'variant__product', 
                'variant__product__store'
            ).all()
            
            if not cart_items.exists():
                return Response({'error': 'Giỏ hàng trống'}, status=400)
        except Cart.DoesNotExist:
            return Response({'error': 'Giỏ hàng trống'}, status=400)

        # 4. Bắt đầu Transaction tạo đơn
        try:
            with transaction.atomic():
                # A. Tạo Order Chính (Master Order) - Khởi tạo sơ bộ
                order = Order.objects.create(
                    buyer=user,
                    address=address,
                    payment_method=payment_method,
                    total_amount=0,     # Sẽ update sau
                    shipping_fee=0,     # Sẽ update sau khi trừ voucher ship
                    discount_amount=0,  # Tổng giảm giá sàn
                    status='pending',
                    payment_status='pending',
                    notes=notes
                )

                # B. Gom nhóm sản phẩm theo Store
                items_by_store = {} 
                for item in cart_items:
                    store = item.variant.product.store 
                    if store not in items_by_store:
                        items_by_store[store] = []
                    items_by_store[store].append(item)

                # Danh sách voucher đã áp dụng thành công để trừ lượt dùng sau này
                # Format: (VoucherObj, DiscountAmount)
                successful_vouchers = []

                # Biến tổng hợp để tính toán
                total_merchandise_after_store_discount = Decimal('0') # Tổng tiền hàng sau khi trừ mã Shop
                
                # ------------------------------------------------------------------
                # C. XỬ LÝ TỪNG SUB-ORDER & ÁP VOUCHER SHOP (Ưu tiên 1)
                # ------------------------------------------------------------------
                for store, items in items_by_store.items():
                    # 1. Tính tổng tiền hàng gốc của Store này
                    store_subtotal_original = sum(item.subtotal for item in items)
                    
                    # 2. Tìm Voucher Shop (nếu user có chọn cho shop này)
                    store_discount = Decimal('0')
                    # Support lấy code theo cả ID chuỗi và ID số
                    store_voucher_code = vouchers_map.get(str(store.pk)) or vouchers_map.get(str(getattr(store, 'store_id', '')))

                    if store_voucher_code:
                        try:
                            # LOCK voucher để tránh race condition
                            sv = Voucher.objects.select_for_update().get(
                                code=store_voucher_code, 
                                scope='store', 
                                is_active=True
                            )
                            # Validate cơ bản
                            now = timezone.now()
                            if not (sv.start_date <= now <= sv.end_date):
                                raise ValidationError(f'Voucher shop {sv.code} đã hết hạn')
                            
                            # Validate Shop ID
                            if sv.store and str(sv.store.pk) != str(store.pk):
                                raise ValidationError(f'Voucher {sv.code} không áp dụng cho shop này')

                            # Validate Min Order
                            if store_subtotal_original < sv.min_order_amount:
                                raise ValidationError(f'Đơn hàng shop {store.name} chưa đạt tối thiểu của voucher')

                            # Validate Usage Limit (Check cả Usage Limit tổng & User Limit)
                            if sv.usage_limit is not None and sv.usage_limit <= 0:
                                raise ValidationError(f'Voucher {sv.code} đã hết lượt')
                            
                            # Check Payment Method Requirement
                            if sv.payment_method_required != 'all':
                                if sv.payment_method_required != payment_method:
                                    raise ValidationError(f'Voucher {sv.code} không áp dụng cho phương thức {payment_method}')

                            # Tính tiền giảm
                            store_discount = calculate_voucher_discount(store_subtotal_original, sv)
                            successful_vouchers.append((sv, store_discount))

                        except Voucher.DoesNotExist:
                            raise ValidationError(f'Voucher shop {store_voucher_code} không tồn tại')

                    # 3. Tính Subtotal sau giảm giá Shop
                    store_subtotal_final = store_subtotal_original - store_discount
                    total_merchandise_after_store_discount += store_subtotal_final

                    # 4. Tạo SubOrder
                    sub_order = SubOrder.objects.create(
                        order=order,
                        store=store,
                        subtotal=store_subtotal_final, # Lưu giá trị sau khi đã trừ Voucher Shop
                        # Nếu model SubOrder có trường store_discount, lưu vào đó:
                        # discount_amount=store_discount, 
                        status='pending'
                    )

                    # 5. Tạo OrderItem và Trừ kho (LOCK KHO)
                    # Gom nhóm variant để lock 1 lần cho hiệu quả
                    variant_ids = [item.variant.pk for item in items]
                    # Lock các dòng variant
                    locked_variants = ProductVariant.objects.select_for_update().filter(pk__in=variant_ids)
                    variant_map = {v.pk: v for v in locked_variants}

                    for item in items:
                        if item.variant.pk not in variant_map:
                             raise ValidationError(f'Sản phẩm {item.variant.sku} không còn tồn tại')
                        
                        pv = variant_map[item.variant.pk]
                        
                        # Check tồn kho
                        if pv.stock < item.quantity:
                            raise ValidationError(f'Sản phẩm {pv.product.name} ({pv.sku}) không đủ hàng (còn {pv.stock})')
                        
                        # Trừ kho
                        pv.stock -= item.quantity
                        pv.save()

                        # Tạo Item
                        OrderItem.objects.create(
                            order=order,
                            sub_order=sub_order,
                            variant=pv,
                            quantity=item.quantity,
                            price_at_order=item.unit_price,
                            discount_amount=0 
                        )

                # ------------------------------------------------------------------
                # D. ÁP VOUCHER SÀN (PLATFORM) (Ưu tiên 2)
                # ------------------------------------------------------------------
                # Voucher sàn tính trên "Tổng tiền hàng sau khi đã trừ Voucher Shop"
                platform_discount_total = Decimal('0')
                platform_code = vouchers_map.get('platform')

                if platform_code:
                    try:
                        pv = Voucher.objects.select_for_update().get(
                            code=platform_code, 
                            scope='platform', 
                            is_active=True
                        )
                        now = timezone.now()
                        if not (pv.start_date <= now <= pv.end_date):
                            raise ValidationError(f'Voucher sàn {platform_code} hết hạn')
                        
                        if total_merchandise_after_store_discount < pv.min_order_amount:
                            raise ValidationError(f'Tổng đơn hàng chưa đạt tối thiểu cho voucher sàn')

                        if pv.usage_limit is not None and pv.usage_limit <= 0:
                            raise ValidationError(f'Voucher sàn {platform_code} đã hết lượt')
                        
                        if pv.payment_method_required != 'all' and pv.payment_method_required != payment_method:
                             raise ValidationError(f'Voucher sàn không áp dụng cho {payment_method}')

                        platform_discount_total = calculate_voucher_discount(total_merchandise_after_store_discount, pv)
                        successful_vouchers.append((pv, platform_discount_total))

                    except Voucher.DoesNotExist:
                        raise ValidationError(f'Voucher sàn {platform_code} không tồn tại')

                # [QUAN TRỌNG] Phân bổ Voucher Sàn (Allocation)
                # Chia ngược tiền giảm giá sàn vào các SubOrder để phục vụ Refund sau này
                if platform_discount_total > 0 and total_merchandise_after_store_discount > 0:
                    remaining_distribute = platform_discount_total
                    sub_orders = SubOrder.objects.filter(order=order) # Query lại trong transaction
                    count = sub_orders.count()

                    for idx, sub in enumerate(sub_orders):
                        if idx == count - 1:
                            # SubOrder cuối cùng chịu phần dư (để tránh lỗi làm tròn)
                            allocated = remaining_distribute
                        else:
                            # Tỷ lệ = Subtotal của Shop / Tổng tiền hàng
                            ratio = sub.subtotal / total_merchandise_after_store_discount
                            allocated = (platform_discount_total * ratio).quantize(Decimal('0.01'))
                        
                        # Lưu vào SubOrder
                        # Kiểm tra xem model SubOrder có trường platform_discount chưa
                        if hasattr(sub, 'platform_discount'):
                            sub.platform_discount = allocated
                            sub.save()
                        
                        remaining_distribute -= allocated

                # ------------------------------------------------------------------
                # E. ÁP VOUCHER VẬN CHUYỂN (Ưu tiên 3)
                # ------------------------------------------------------------------
                final_shipping_fee = shipping_fee_req
                shipping_discount = Decimal('0')
                shipping_code = vouchers_map.get('shipping')

                if shipping_code:
                    try:
                        sv = Voucher.objects.select_for_update().get(
                            code=shipping_code, 
                            is_active=True
                        )
                        # Check scope (shipping hoặc platform hỗ trợ freeship)
                        if sv.scope != 'shipping' and not getattr(sv, 'is_free_shipping', False):
                             # Fallback: cho phép voucher platform dùng làm shipping nếu nó có cờ freeship
                             if sv.scope != 'platform':
                                raise ValidationError(f'Mã {shipping_code} không phải voucher vận chuyển')

                        now = timezone.now()
                        if not (sv.start_date <= now <= sv.end_date):
                            raise ValidationError(f'Voucher vận chuyển hết hạn')
                        
                        # Min order check cho shipping thường dựa trên tổng giá trị đơn hàng
                        if total_merchandise_after_store_discount < sv.min_order_amount:
                             raise ValidationError(f'Chưa đủ điều kiện freeship')

                        if sv.usage_limit is not None and sv.usage_limit <= 0:
                            raise ValidationError(f'Voucher vận chuyển đã hết lượt')
                        
                        if sv.payment_method_required != 'all' and sv.payment_method_required != payment_method:
                             raise ValidationError(f'Voucher ship không áp dụng cho {payment_method}')

                        # [SỬA LẠI LOGIC TÍNH TIỀN SHIP]
                        # 1. Tính giảm giá dựa trên discount_value trước (ví dụ giảm 30k)
                        shipping_discount = calculate_voucher_discount(final_shipping_fee, sv)
                        
                        # 2. Nếu tính ra 0đ (do admin không nhập value) 
                        # NHƯNG voucher có bật cờ "is_free_shipping" -> Thì mới Free 100%
                        if shipping_discount == 0 and getattr(sv, 'is_free_shipping', False):
                            shipping_discount = final_shipping_fee
                        
                        # 3. Đảm bảo không giảm quá số tiền ship thực tế
                        shipping_discount = min(shipping_discount, final_shipping_fee)
                        
                        # Lưu vào danh sách thành công
                        successful_vouchers.append((sv, shipping_discount))
                        
                        # Cập nhật phí ship cuối cùng
                        final_shipping_fee = final_shipping_fee - shipping_discount
                        if final_shipping_fee < 0: final_shipping_fee = Decimal('0')

                    except Voucher.DoesNotExist:
                        raise ValidationError(f'Voucher vận chuyển {shipping_code} không tồn tại')

                # ------------------------------------------------------------------
                # F. TỔNG KẾT & LƯU ORDER
                # ------------------------------------------------------------------
                
                # Tổng tiền khách phải trả = (Hàng sau Voucher Shop) - (Voucher Sàn) + (Ship sau Voucher)
                final_total_amount = total_merchandise_after_store_discount - platform_discount_total + final_shipping_fee
                
                if final_total_amount < 0:
                    final_total_amount = Decimal('0')

                order.total_amount = final_total_amount
                order.shipping_fee = final_shipping_fee
                order.discount_amount = platform_discount_total # Chỉ lưu discount sàn vào field này
                order.save()

                # ------------------------------------------------------------------
                # G. TRỪ LƯỢT DÙNG VOUCHER (Common Logic)
                # ------------------------------------------------------------------
                for voucher, amount in successful_vouchers:
                    # 1. Trừ usage_limit
                    if voucher.usage_limit is not None:
                        voucher.usage_limit -= 1
                        voucher.save()
                    
                    # 2. Check & Update User Limit
                    uv, _ = UserVoucher.objects.get_or_create(user=user, voucher=voucher)
                    
                    # Kiểm tra Reservation (nếu có dùng API reserve trước đó)
                    reservation = VoucherReservation.objects.filter(user=user, voucher=voucher).first()
                    if reservation:
                        reservation.delete() 
                    
                    # Check Per User Limit
                    usage_record, _ = VoucherUsage.objects.get_or_create(user=user, voucher=voucher)
                    
                    if usage_record.used_count >= voucher.per_user_limit:
                         raise ValidationError(f'Bạn đã hết lượt dùng voucher {voucher.code}')
                    
                    usage_record.used_count += 1
                    usage_record.last_used_at = timezone.now()
                    usage_record.save()

                    # Update UserVoucher (Ví) để hiển thị UI
                    uv.used_count += 1
                    uv.save()

                    # 3. Lưu lịch sử OrderVoucher
                    OrderVoucher.objects.create(
                        order=order,
                        voucher=voucher,
                        discount_amount=amount
                    )
                    
                    # Log
                    try:
                        logs_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs.txt')
                        with open(logs_path, 'a', encoding='utf-8') as lf:
                            lf.write(f"{timezone.now().isoformat()} USE voucher={voucher.code} user={user.id} order={order.order_id} discount={amount}\n")
                    except: pass

                # Xóa giỏ hàng
                cart.items.all().delete()

                # Gửi thông báo
                try:
                    notify_order_created(user, order.order_id)
                except Exception as e:
                    print(f"Notification Error: {str(e)}")

                # Tạo link thanh toán
                payment_url = None
                if payment_method == "VNPAY":
                    relative_path = f"/payments/vnpay/{order.order_id}/"
                    payment_url = request.build_absolute_uri(relative_path)
                elif payment_method == "PAYPAL":
                    relative_path = f"/payments/paypal/{order.order_id}/"
                    payment_url = request.build_absolute_uri(relative_path)

                return Response({
                    'message': 'Đặt hàng thành công',
                    'order_id': order.order_id,
                    'total_amount': order.total_amount,
                    'payment_url': payment_url 
                }, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            # Catch Validation Error explicitly to return 400
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Create Order Error: {str(e)}")
            return Response({'error': f"Lỗi xử lý đơn hàng: {str(e)}"}, status=500)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel order - allowed for pending/processing with conditions"""
        order = self.get_object()
        
        # Check permissions
        is_buyer = order.buyer == request.user
        is_shop = request.user.is_staff
        
        if not (is_buyer or is_shop):
            return Response({'error': 'Bạn không có quyền hủy đơn hàng này'}, status=status.HTTP_403_FORBIDDEN)
        
        if order.status not in ['pending', 'processing']:
            return Response({'error': 'Không thể hủy đơn hàng đang giao hoặc đã hoàn thành.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if order.status == 'processing' and is_buyer and not is_shop:
            return Response({'error': 'Đơn hàng đang xử lý. Vui lòng liên hệ shop.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Bắt đầu rollback
        try:
            with transaction.atomic():
                order.status = 'cancelled'
                refund_message = ''
                if order.payment_status == 'paid':
                    order.payment_status = 'refunded'
                    refund_message = ' Tiền sẽ được hoàn trong 5-7 ngày làm việc.'
                
                order.save()
                
                # 1. Hoàn Tồn kho
                for sub_order in order.sub_orders.all():
                    for item in sub_order.items.all():
                        # Lock variant để cộng lại
                        variant = ProductVariant.objects.select_for_update().get(pk=item.variant.pk)
                        variant.stock += item.quantity
                        variant.save()

                # 2. Hoàn Voucher (Usage Limit & User Limit)
                for ov in order.order_vouchers.all():
                    v = ov.voucher
                    # Lock voucher
                    v_locked = Voucher.objects.select_for_update().get(pk=v.pk)
                    
                    if v_locked.usage_limit is not None:
                        v_locked.usage_limit += 1
                        v_locked.save()

                    # Hoàn User Usage
                    try:
                        vu = VoucherUsage.objects.get(user=order.buyer, voucher=v_locked)
                        if vu.used_count > 0:
                            vu.used_count -= 1
                            vu.save()
                    except VoucherUsage.DoesNotExist:
                        pass
                    
                    # Hoàn UserVoucher (Ví)
                    try:
                        uv = UserVoucher.objects.get(user=order.buyer, voucher=v_locked)
                        if uv.used_count > 0:
                            uv.used_count -= 1
                            uv.save()
                    except UserVoucher.DoesNotExist:
                        pass

                    # Log restore
                    try:
                        logs_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs.txt')
                        with open(logs_path, 'a', encoding='utf-8') as lf:
                            lf.write(f"{timezone.now().isoformat()} RESTORE voucher={v.code} user={order.buyer.id} order={order.order_id}\n")
                    except: pass

                # Send notification
                try:
                    notify_order_status_update(order.buyer, order.order_id, 'cancelled')
                except: pass
                
                return Response({
                    'success': True,
                    'message': f'Đã hủy đơn hàng thành công.{refund_message}'
                }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': f'Lỗi hủy đơn: {str(e)}'}, status=500)

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Shop confirm order"""
        order = self.get_object()
        
        if not request.user.is_staff:
            return Response({'error': 'Chỉ shop mới có thể xác nhận đơn hàng'}, status=status.HTTP_403_FORBIDDEN)
        
        if order.status != 'pending':
            return Response({'error': 'Chỉ có thể xác nhận đơn hàng đang chờ duyệt'}, status=status.HTTP_400_BAD_REQUEST)
        
        order.status = 'processing'
        order.save()
        order.sub_orders.all().update(status='processing')

        try:
            notify_order_status_update(order.buyer, order.order_id, 'confirmed')
        except: pass

        return Response({'success': True, 'message': 'Đã xác nhận đơn hàng'}, status=status.HTTP_200_OK)