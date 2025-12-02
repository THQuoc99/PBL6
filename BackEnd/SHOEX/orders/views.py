from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from decimal import Decimal

# Import Models
from .models import Order, SubOrder, OrderItem
from .serializers import OrderSerializer
from cart.models import Cart
from address.models import Address

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
                    shipping_fee=0,
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
                    
                    # Tạo OrderItem và Trừ tồn kho
                    for item in items:
                        OrderItem.objects.create(
                            order=order,
                            sub_order=sub_order,
                            variant=item.variant,
                            quantity=item.quantity,
                            price_at_order=item.unit_price,
                            discount_amount=0
                        )
                        
                        # Trừ tồn kho
                        item.variant.stock -= item.quantity
                        item.variant.save()
                    
                    total_order_amount += sub_total

                # D. Cập nhật tổng tiền cho Order chính
                # Có thể cộng thêm shipping_fee nếu có logic tính phí vận chuyển
                order.total_amount = total_order_amount + order.shipping_fee
                order.save()

                # E. Xóa giỏ hàng sau khi đặt thành công
                cart.items.all().delete()

                # F. Tạo link thanh toán (Nếu không phải COD)
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