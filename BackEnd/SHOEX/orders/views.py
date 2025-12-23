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

# Import Models
from .models import Order, SubOrder, OrderItem
from .serializers import OrderSerializer
from cart.models import Cart
from products.models import ProductVariant
from address.models import Address
from discount.models import Voucher, OrderVoucher, UserVoucher, VoucherReservation, VoucherUsage

# Import notification helpers
from notifications.utils import notify_order_created, notify_order_status_update

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
        shipping_fee = Decimal(str(request.data.get('shipping_fee', 0)))
        notes = request.data.get('notes', '')
        user = request.user

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
            # Load trước các quan hệ để tối ưu query: Variant -> Product -> Store
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
                # A. Tạo Order Chính (Master Order)
                order = Order.objects.create(
                    buyer=user,
                    address=address,
                    payment_method=payment_method,
                    total_amount=0, # Sẽ cập nhật sau khi cộng tổng SubOrder
                    status='pending',
                    payment_status='pending',
                    shipping_fee=shipping_fee,
                    notes=notes
                )

                total_order_amount = Decimal(0)
                
                # B. Gom nhóm sản phẩm theo Store (Cửa hàng)
                items_by_store = {} 
                for item in cart_items:
                    store = item.variant.product.store 
                    if store not in items_by_store:
                        items_by_store[store] = []
                    items_by_store[store].append(item)

                # C. Tạo SubOrder cho từng Store
                for store, items in items_by_store.items():
                    # Tính tổng tiền cho SubOrder này
                    sub_total = sum(item.subtotal for item in items)
                    
                    # Tạo SubOrder
                    sub_order = SubOrder.objects.create(
                        order=order,
                        store=store,
                        subtotal=sub_total,
                        status='pending'
                    )
                    
                    # Kiểm tra tồn kho cho tất cả item trước khi tạo OrderItem/ghi giảm
                    locked_variants = {}
                    for item in items:
                        try:
                            pv = ProductVariant.objects.select_for_update().get(pk=item.variant.pk)
                        except ProductVariant.DoesNotExist:
                            # Raise lỗi để Transaction tự rollback toàn bộ đơn hàng
                            raise ValidationError({'error': f'Biến thể không tồn tại (variant id {item.variant.pk})'})

                        if pv.stock < item.quantity:
                            sku = getattr(pv, 'sku', str(pv.pk))
                            # Raise lỗi để Transaction tự rollback (trả lại hàng cho Store 1 nếu Store 2 lỗi)
                            raise ValidationError({'error': f'Sản phẩm {sku} không đủ hàng'})

                        locked_variants[item.variant.pk] = pv

                    # Nếu đủ hàng, tạo OrderItem và trừ tồn kho
                    for item in items:
                        pv = locked_variants.get(item.variant.pk)
                        OrderItem.objects.create(
                            order=order,
                            sub_order=sub_order,
                            variant=item.variant,
                            quantity=item.quantity,
                            price_at_order=item.unit_price,
                            discount_amount=0
                        )
                        pv.stock = pv.stock - item.quantity
                        pv.save()
                    
                    total_order_amount += sub_total

                # D. Áp voucher nếu có
                # Hỗ trợ 2 dạng input từ frontend:
                # - 'vouchers' là mapping {"<store_id>": "VOUCHERCODE", "platform": "PLATFORMCODE"}
                # - fallback: 'voucher_code' áp cho toàn bộ đơn như trước
                total_amount_temp = total_order_amount
                discount_amount = Decimal('0')

                vouchers_map = request.data.get('vouchers')
                fallback_voucher_code = request.data.get('voucher_code')

                applied_vouchers = []

                if vouchers_map:
                    # Áp voucher theo từng SubOrder (store)
                    platform_code = None
                    parsed_map = None
                    if isinstance(vouchers_map, dict):
                        parsed_map = vouchers_map
                    else:
                        try:
                            import json
                            parsed_map = json.loads(vouchers_map)
                        except Exception:
                            parsed_map = {}

                    # Lưu platform and shipping code nếu có — sẽ áp một lần sau khi xử lý store vouchers
                    platform_code = parsed_map.get('platform')
                    shipping_code = parsed_map.get('shipping')

                    for sub_order in order.sub_orders.all():
                        store_key = str(sub_order.store.pk)
                        voucher_code = parsed_map.get(store_key)

                        if not voucher_code:
                            continue

                        try:
                            voucher = Voucher.objects.select_for_update().get(code=voucher_code, is_active=True)
                            now = timezone.now().date()
                            if voucher.start_date > now or voucher.end_date < now:
                                return Response({'error': f'Voucher {voucher_code} hết hạn hoặc chưa đến hạn'}, status=400)

                            if voucher.usage_limit and voucher.usage_limit <= 0:
                                return Response({'error': f'Voucher {voucher_code} đã hết lượt sử dụng'}, status=400)

                            uv = UserVoucher.objects.filter(user=user, voucher=voucher).first()
                            if uv and uv.used_count >= voucher.per_user_limit:
                                return Response({'error': f'Bạn đã sử dụng voucher {voucher_code} quá giới hạn'}, status=400)
                            # Persistent per-user usage check
                            vup_check = VoucherUsage.objects.filter(user=user, voucher=voucher).first()
                            if vup_check and vup_check.used_count >= voucher.per_user_limit:
                                return Response({'error': f'Bạn đã sử dụng voucher {voucher_code} quá giới hạn'}, status=400)

                            # Tính giảm cho sub_order
                            sub_total = Decimal(sub_order.subtotal)
                            sub_discount = Decimal('0')
                            if voucher.discount_type == 'fixed':
                                sub_discount = Decimal(voucher.discount_value)
                            else:
                                sub_discount = (sub_total * Decimal(voucher.discount_value)) / Decimal('100')
                                if voucher.max_discount:
                                    sub_discount = min(sub_discount, Decimal(voucher.max_discount))

                            if sub_discount > sub_total:
                                sub_discount = sub_total

                            # Cập nhật counters: nếu có reservation cho user thì consume reservation
                            reservation = VoucherReservation.objects.filter(voucher=voucher, user=user).first()
                            if reservation:
                                reservation.delete()
                            else:
                                if voucher.usage_limit:
                                    voucher.usage_limit = int(voucher.usage_limit) - 1
                                    voucher.save()

                            if uv:
                                uv.used_count = uv.used_count + 1
                                uv.save()

                            # Persist per-user usage for stronger enforcement
                            try:
                                vu, _created = VoucherUsage.objects.get_or_create(voucher=voucher, user=user)
                                vu.used_count = vu.used_count + 1
                                vu.last_used_at = timezone.now()
                                vu.save()
                            except Exception:
                                pass

                            if getattr(voucher, 'is_free_shipping', False):
                                order.shipping_fee = Decimal('0')

                            try:
                                ov = OrderVoucher.objects.create(order=order, voucher=voucher, discount_amount=sub_discount)
                                try:
                                    logs_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs.txt')
                                    with open(logs_path, 'a', encoding='utf-8') as lf:
                                        lf.write(f"{timezone.now().isoformat()} USE voucher={voucher.code} user={user.id} order={order.order_id} discount={sub_discount}\n")
                                except Exception:
                                    pass
                            except Exception as e:
                                print(f"OrderVoucher create error: {e}")

                            discount_amount += sub_discount
                            applied_vouchers.append(voucher_code)

                        except Voucher.DoesNotExist:
                            return Response({'error': f'Voucher {voucher_code} không hợp lệ'}, status=400)

                    # Áp voucher platform một lần trên phần còn lại (nếu có)
                    if platform_code:
                        try:
                            pv = Voucher.objects.select_for_update().get(code=platform_code, is_active=True)
                            now = timezone.now().date()
                            if pv.start_date > now or pv.end_date < now:
                                return Response({'error': f'Platform voucher {platform_code} hết hạn hoặc chưa đến hạn'}, status=400)

                            remaining_total = total_amount_temp - discount_amount
                            if remaining_total <= 0:
                                # Không còn tiền để giảm
                                platform_discount = Decimal('0')
                            else:
                                if pv.discount_type == 'fixed':
                                    platform_discount = Decimal(pv.discount_value)
                                else:
                                    platform_discount = (remaining_total * Decimal(pv.discount_value)) / Decimal('100')
                                    if pv.max_discount:
                                        platform_discount = min(platform_discount, Decimal(pv.max_discount))

                                if platform_discount > remaining_total:
                                    platform_discount = remaining_total

                            if pv.usage_limit and pv.usage_limit <= 0:
                                return Response({'error': f'Platform voucher {platform_code} đã hết lượt sử dụng'}, status=400)

                            uvp = UserVoucher.objects.filter(user=user, voucher=pv).first()
                            if uvp and uvp.used_count >= pv.per_user_limit:
                                return Response({'error': f'Bạn đã sử dụng platform voucher {platform_code} quá giới hạn'}, status=400)
                            # Persistent per-user usage check for platform voucher
                            vup_check_p = VoucherUsage.objects.filter(user=user, voucher=pv).first()
                            if vup_check_p and vup_check_p.used_count >= pv.per_user_limit:
                                return Response({'error': f'Bạn đã sử dụng platform voucher {platform_code} quá giới hạn'}, status=400)

                            # Áp freeship nếu có
                            if getattr(pv, 'is_free_shipping', False):
                                order.shipping_fee = Decimal('0')

                            # Cập nhật counters: nếu có reservation cho user thì consume reservation
                            pres = VoucherReservation.objects.filter(voucher=pv, user=user).first()
                            if pres:
                                pres.delete()
                            else:
                                if pv.usage_limit:
                                    pv.usage_limit = int(pv.usage_limit) - 1
                                    pv.save()
                            if uvp:
                                uvp.used_count = uvp.used_count + 1
                                uvp.save()

                            # Persist per-user usage for platform voucher
                            try:
                                vup, _created = VoucherUsage.objects.get_or_create(voucher=pv, user=user)
                                vup.used_count = vup.used_count + 1
                                vup.last_used_at = timezone.now()
                                vup.save()
                            except Exception:
                                pass

                            if platform_discount > 0:
                                try:
                                    ov = OrderVoucher.objects.create(order=order, voucher=pv, discount_amount=platform_discount)
                                    try:
                                        logs_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs.txt')
                                        with open(logs_path, 'a', encoding='utf-8') as lf:
                                            lf.write(f"{timezone.now().isoformat()} USE voucher={pv.code} user={user.id} order={order.order_id} discount={platform_discount}\n")
                                    except Exception:
                                        pass
                                except Exception as e:
                                    print(f"OrderVoucher create error: {e}")
                                discount_amount += platform_discount
                                applied_vouchers.append(platform_code)
                        except Voucher.DoesNotExist:
                            return Response({'error': f'Platform voucher {platform_code} không hợp lệ'}, status=400)

                    # Áp voucher shipping (chỉ ảnh hưởng đến shipping_fee)
                    if shipping_code:
                        try:
                            sv = Voucher.objects.select_for_update().get(code=shipping_code, is_active=True)
                            now = timezone.now().date()
                            if sv.start_date > now or sv.end_date < now:
                                return Response({'error': f'Shipping voucher {shipping_code} hết hạn hoặc chưa đến hạn'}, status=400)

                            # shipping vouchers should be of type 'shipping' or be marked is_free_shipping
                            if sv.type != 'shipping' and not getattr(sv, 'is_free_shipping', False):
                                # allow platform voucher marked as free shipping as backward-compatibility
                                if sv.type != 'platform':
                                    return Response({'error': f'Voucher {shipping_code} không phải voucher giao hàng'}, status=400)

                            # compute shipping discount
                            shipping_discount = Decimal('0')
                            if getattr(sv, 'is_free_shipping', False):
                                shipping_discount = order.shipping_fee
                            else:
                                if sv.discount_type == 'fixed':
                                    shipping_discount = Decimal(sv.discount_value)
                                else:
                                    shipping_discount = (order.shipping_fee * Decimal(sv.discount_value)) / Decimal('100')
                                    if sv.max_discount:
                                        shipping_discount = min(shipping_discount, Decimal(sv.max_discount))

                            if shipping_discount > order.shipping_fee:
                                shipping_discount = order.shipping_fee

                            # usage checks
                            if sv.usage_limit and sv.usage_limit <= 0:
                                return Response({'error': f'Shipping voucher {shipping_code} đã hết lượt sử dụng'}, status=400)

                            uvp = UserVoucher.objects.filter(user=user, voucher=sv).first()
                            if uvp and uvp.used_count >= sv.per_user_limit:
                                return Response({'error': f'Bạn đã sử dụng shipping voucher {shipping_code} quá giới hạn'}, status=400)

                            vup_check_p = VoucherUsage.objects.filter(user=user, voucher=sv).first()
                            if vup_check_p and vup_check_p.used_count >= sv.per_user_limit:
                                return Response({'error': f'Bạn đã sử dụng shipping voucher {shipping_code} quá giới hạn'}, status=400)

                            # consume reservation or decrement usage
                            pres = VoucherReservation.objects.filter(voucher=sv, user=user).first()
                            if pres:
                                pres.delete()
                            else:
                                if sv.usage_limit:
                                    sv.usage_limit = int(sv.usage_limit) - 1
                                    sv.save()

                            if uvp:
                                uvp.used_count = uvp.used_count + 1
                                uvp.save()

                            try:
                                vup, _created = VoucherUsage.objects.get_or_create(voucher=sv, user=user)
                                vup.used_count = vup.used_count + 1
                                vup.last_used_at = timezone.now()
                                vup.save()
                            except Exception:
                                pass

                            # apply discount to order.shipping_fee
                            order.shipping_fee = order.shipping_fee - shipping_discount
                            if order.shipping_fee < 0:
                                order.shipping_fee = Decimal('0')

                            # record OrderVoucher
                            try:
                                ov = OrderVoucher.objects.create(order=order, voucher=sv, discount_amount=shipping_discount)
                            except Exception:
                                pass

                            discount_amount += shipping_discount
                            applied_vouchers.append(shipping_code)

                        except Voucher.DoesNotExist:
                            return Response({'error': f'Shipping voucher {shipping_code} không hợp lệ'}, status=400)
                        except Voucher.DoesNotExist:
                            return Response({'error': f'Platform voucher {platform_code} không hợp lệ'}, status=400)

                elif fallback_voucher_code:
                    # fallback: apply on whole order like trước
                    voucher_code = fallback_voucher_code
                    try:
                        voucher = Voucher.objects.select_for_update().get(code=voucher_code, is_active=True)
                        now = timezone.now().date()
                        if voucher.start_date > now or voucher.end_date < now:
                            return Response({'error': 'Voucher hết hạn hoặc chưa đến hạn'}, status=400)

                        if total_amount_temp < voucher.min_order_amount:
                            return Response({'error': f"Đơn hàng chưa đạt tối thiểu {voucher.min_order_amount:,.0f}đ"}, status=400)

                        if voucher.usage_limit and voucher.usage_limit <= 0:
                            return Response({'error': 'Voucher đã hết lượt sử dụng'}, status=400)

                        uv = UserVoucher.objects.filter(user=user, voucher=voucher).first()
                        if uv and uv.used_count >= voucher.per_user_limit:
                            return Response({'error': 'Bạn đã sử dụng voucher này quá giới hạn'}, status=400)
                            # Persistent per-user usage check
                            vup_check_f = VoucherUsage.objects.filter(user=user, voucher=voucher).first()
                            if vup_check_f and vup_check_f.used_count >= voucher.per_user_limit:
                                return Response({'error': 'Bạn đã sử dụng voucher này quá giới hạn'}, status=400)

                        if voucher.discount_type == 'fixed':
                            discount_amount = Decimal(voucher.discount_value)
                        else:
                            discount_amount = (total_amount_temp * Decimal(voucher.discount_value)) / Decimal('100')
                            if voucher.max_discount:
                                discount_amount = min(discount_amount, Decimal(voucher.max_discount))

                        if discount_amount > total_amount_temp:
                            discount_amount = total_amount_temp

                        # Cập nhật counters: nếu có reservation thì consume, ngược lại giảm usage_limit
                        reservation = VoucherReservation.objects.filter(voucher=voucher, user=user).first()
                        if reservation:
                            reservation.delete()
                        else:
                            if voucher.usage_limit:
                                voucher.usage_limit = int(voucher.usage_limit) - 1
                                voucher.save()

                        if uv:
                            uv.used_count = uv.used_count + 1
                            uv.save()

                        # Persist per-user usage for fallback voucher
                        try:
                            vuf, _created = VoucherUsage.objects.get_or_create(voucher=voucher, user=user)
                            vuf.used_count = vuf.used_count + 1
                            vuf.last_used_at = timezone.now()
                            vuf.save()
                        except Exception:
                            pass

                        if getattr(voucher, 'is_free_shipping', False):
                            order.shipping_fee = Decimal('0')

                    except Voucher.DoesNotExist:
                        return Response({'error': 'Voucher không hợp lệ'}, status=400)

                # D. Cập nhật tổng tiền cho Order chính
                # Áp discount (nếu có) trước khi cộng phí vận chuyển
                order.discount_amount = discount_amount
                order.total_amount = total_amount_temp - discount_amount + order.shipping_fee
                order.save()

                # G. (Đã tạo OrderVoucher cho từng voucher trong quá trình xử lý)
                # E. Xóa giỏ hàng sau khi đặt thành công
                cart.items.all().delete()

                # F. Tạo thông báo cho user
                try:
                    notify_order_created(user, order.order_id)
                except Exception as e:
                    print(f"Notification Error: {str(e)}")
                    # Không làm fail transaction nếu notification lỗi

                # G. Tạo link thanh toán (Nếu không phải COD)
                payment_url = None
                
                if payment_method == "VNPAY":
                    relative_path = f"/payments/vnpay/{order.order_id}/"
                    payment_url = request.build_absolute_uri(relative_path)
                
                elif payment_method == "PAYPAL":
                    relative_path = f"/payments/paypal/{order.order_id}/"
                    payment_url = request.build_absolute_uri(relative_path)

                # Trả về kết quả
                return Response({
                    'message': 'Đặt hàng thành công',
                    'order_id': order.order_id,
                    'total_amount': order.total_amount,
                    'payment_url': payment_url 
                }, status=status.HTTP_201_CREATED)

        except Exception as e:
            # Log lỗi ra console server để debug nếu cần
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
            return Response({
                'error': 'Bạn không có quyền hủy đơn hàng này'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Cannot cancel shipped/completed orders
        if order.status not in ['pending', 'processing']:
            return Response({
                'error': 'Không thể hủy đơn hàng đang giao hoặc đã hoàn thành. Vui lòng yêu cầu trả hàng.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # If processing, only shop can cancel (buyer needs shop approval)
        if order.status == 'processing' and is_buyer and not is_shop:
            return Response({
                'error': 'Đơn hàng đang được xử lý. Vui lòng liên hệ shop để yêu cầu hủy đơn.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update order status
        order.status = 'cancelled'
        
        # Refund if already paid
        refund_message = ''
        if order.payment_status == 'paid':
            order.payment_status = 'refunded'
            refund_message = ' Tiền sẽ được hoàn trong 5-7 ngày làm việc.'
            # TODO: Call VNPay/PayPal refund API here when integrated
        
        order.save()
        
        # Restore stock for all items
        for sub_order in order.sub_orders.all():
            for item in sub_order.items.all():
                item.variant.stock += item.quantity
                item.variant.save()

        # Hoàn lại usage_limit và UserVoucher.used_count cho các voucher đã được áp vào đơn
        try:
            for ov in order.order_vouchers.all():
                v = ov.voucher
                # restore usage_limit nếu có
                if v.usage_limit is not None:
                    v.usage_limit = int(v.usage_limit) + 1
                    v.save()

                # giảm used_count trong user wallet nếu có
                uv = UserVoucher.objects.filter(user=order.buyer, voucher=v).first()
                if uv and uv.used_count > 0:
                    uv.used_count = uv.used_count - 1
                    uv.save()
                    # giảm VoucherUsage nếu có
                    try:
                        vu = VoucherUsage.objects.filter(voucher=v, user=order.buyer).first()
                        if vu and vu.used_count > 0:
                            vu.used_count = vu.used_count - 1
                            vu.last_used_at = timezone.now()
                            vu.save()
                    except Exception:
                        pass
                # Log restore
                try:
                    logs_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs.txt')
                    with open(logs_path, 'a', encoding='utf-8') as lf:
                        lf.write(f"{timezone.now().isoformat()} RESTORE voucher={v.code} user={order.buyer.id} order={order.order_id} restored_amount={ov.discount_amount}\n")
                except Exception:
                    pass
        except Exception as e:
            print(f"Error restoring voucher counters on cancel: {e}")
        
        # Send notification
        try:
            notify_order_status_update(order.buyer, order.order_id, 'cancelled')
        except Exception as e:
            print(f"Notification Error: {str(e)}")
        
        return Response({
            'success': True,
            'message': f'Đã hủy đơn hàng thành công.{refund_message}'
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Shop confirm order - change pending to processing"""
        order = self.get_object()
        
        # Only shop/admin can confirm
        if not request.user.is_staff:
            return Response({
                'error': 'Chỉ shop mới có thể xác nhận đơn hàng'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Only allow confirming pending orders
        if order.status != 'pending':
            return Response({
                'error': 'Chỉ có thể xác nhận đơn hàng đang chờ duyệt'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update order status to processing
        order.status = 'processing'
        order.save()
        
        # Update all sub_orders
        order.sub_orders.all().update(status='processing')

        # Send notification
        try:
            notify_order_status_update(order.buyer, order.order_id, 'confirmed')
        except Exception as e:
            print(f"Notification Error: {str(e)}")

        return Response({
            'success': True,
            'message': 'Đã xác nhận đơn hàng'
        }, status=status.HTTP_200_OK)