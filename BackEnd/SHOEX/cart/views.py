from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Cart, CartItem
from products.models import ProductVariant
from .serializers import CartSerializer

class CartViewSet(viewsets.ViewSet):
    # Cho phép cả User đăng nhập và Guest (nếu bạn muốn làm guest cart sau này)
    # Hiện tại ưu tiên User đã đăng nhập
    permission_classes = [IsAuthenticated]

    def get_cart(self, request):
        # Lấy hoặc tạo giỏ hàng cho user
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return cart

    def list(self, request):
        """Xem giỏ hàng"""
        cart = self.get_cart(request)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def add(self, request):
        """Thêm sản phẩm (Variant) vào giỏ"""
        # Flutter gửi lên: { "variant_id": 1, "quantity": 1 }
        variant_id = request.data.get('variant_id')
        quantity = int(request.data.get('quantity', 1))

        if not variant_id:
            return Response({'error': 'Thiếu variant_id'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            variant = ProductVariant.objects.get(pk=variant_id, is_active=True)
            
            if variant.stock < quantity:
                 return Response({'error': 'Sản phẩm không đủ hàng'}, status=status.HTTP_400_BAD_REQUEST)

            cart = self.get_cart(request)

            # Kiểm tra item đã có chưa
            item, created = CartItem.objects.get_or_create(
                cart=cart, 
                variant=variant,
                defaults={'unit_price': variant.price, 'quantity': 0}
            )
            
            # Cộng dồn số lượng
            item.quantity += quantity
            item.unit_price = variant.price # Cập nhật giá mới nhất
            item.save()

            # Cập nhật timestamp cho Cart
            cart.save() 

            return Response({'message': 'Đã thêm vào giỏ', 'cart_count': cart.items.count()})
            
        except ProductVariant.DoesNotExist:
            return Response({'error': 'Sản phẩm không tồn tại'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['patch'])
    def update_quantity(self, request, pk=None):
        """Sửa số lượng (pk là item_id)"""
        # Flutter gửi: PATCH /api/cart/{item_id}/update_quantity/ body: {"quantity": 5}
        try:
            quantity = int(request.data.get('quantity', 1))
            cart = self.get_cart(request)
            item = CartItem.objects.get(pk=pk, cart=cart)

            if quantity <= 0:
                item.delete()
            else:
                # Check tồn kho
                if quantity > item.variant.stock:
                    return Response({'error': f'Chỉ còn {item.variant.stock} sản phẩm'}, status=400)
                
                item.quantity = quantity
                item.save()
            
            # Trả về giỏ hàng mới nhất để update UI
            serializer = CartSerializer(cart)
            return Response(serializer.data)

        except CartItem.DoesNotExist:
            return Response({'error': 'Item không tìm thấy'}, status=404)

    @action(detail=True, methods=['delete'])
    def remove(self, request, pk=None):
        """Xóa item"""
        try:
            cart = self.get_cart(request)
            item = CartItem.objects.get(pk=pk, cart=cart)
            item.delete()
            
            # Trả về giỏ hàng mới
            serializer = CartSerializer(cart)
            return Response(serializer.data)
        except CartItem.DoesNotExist:
            return Response({'error': 'Item không tìm thấy'}, status=404)