from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

# Import Models
from .models import Cart, CartItem, Wishlist
from products.models import Product, ProductVariant

# Import Serializers
from .serializers import CartSerializer
from products.serializers import ProductSerializer

# ==============================================================================
# CART VIEWSET (Xử lý Giỏ hàng)
# ==============================================================================
class CartViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def get_cart(self, request):
        """Helper: Lấy hoặc tạo giỏ hàng cho user"""
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return cart

    def list(self, request):
        """GET /api/cart/ - Xem giỏ hàng"""
        cart = self.get_cart(request)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def add(self, request):
        """POST /api/cart/add/ - Thêm sản phẩm vào giỏ"""
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
        """PATCH /api/cart/{item_id}/update_quantity/ - Sửa số lượng"""
        try:
            # Debug logging
            print(f"Update quantity called - item_id: {pk}, data: {request.data}")
            
            # Validate quantity parameter
            if 'quantity' not in request.data:
                print(f"ERROR: Missing quantity in request data: {request.data}")
                return Response({'error': 'Thiếu tham số quantity'}, status=400)
            
            try:
                quantity = int(request.data.get('quantity'))
            except (ValueError, TypeError) as e:
                print(f"ERROR: Invalid quantity value: {request.data.get('quantity')}, error: {e}")
                return Response({'error': 'Quantity phải là số nguyên'}, status=400)
            
            cart = self.get_cart(request)
            item = CartItem.objects.get(pk=pk, cart=cart)

            if quantity <= 0:
                item.delete()
            else:
                # Check tồn kho
                print(f"Stock check: requested={quantity}, available={item.variant.stock}")
                if quantity > item.variant.stock:
                    error_msg = f'Chỉ còn {item.variant.stock} sản phẩm'
                    print(f"ERROR: {error_msg}")
                    return Response({'error': error_msg}, status=400)
                
                item.quantity = quantity
                item.save()
                print(f"Updated successfully: item {pk} -> quantity {quantity}")
            
            # Trả về giỏ hàng mới nhất để update UI
            serializer = CartSerializer(cart)
            return Response(serializer.data)

        except CartItem.DoesNotExist:
            return Response({'error': 'Item không tìm thấy'}, status=404)

    @action(detail=True, methods=['delete'])
    def remove(self, request, pk=None):
        """DELETE /api/cart/{item_id}/remove/ - Xóa item"""
        try:
            cart = self.get_cart(request)
            item = CartItem.objects.get(pk=pk, cart=cart)
            item.delete()
            
            # Trả về giỏ hàng mới
            serializer = CartSerializer(cart)
            return Response(serializer.data)
        except CartItem.DoesNotExist:
            return Response({'error': 'Item không tìm thấy'}, status=404)


# ==============================================================================
# WISHLIST APIs (Xử lý Yêu thích)
# ==============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_wishlist(request):
    """
    GET /api/cart/wishlist/
    Lấy danh sách sản phẩm yêu thích (trả về danh sách Product unique).
    """
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('variant__product')
    
    product_list = []
    seen_ids = set()
    
    for item in wishlist_items:
        product = item.variant.product
        # Lọc trùng lặp product_id
        if product.product_id not in seen_ids:
            product_list.append(product)
            seen_ids.add(product.product_id)
            
    serializer = ProductSerializer(product_list, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_wishlist_api(request):
    """
    POST /api/cart/wishlist/toggle/
    Thêm/Xóa yêu thích dựa trên product_id.
    Backend tự tìm variant đại diện để lưu.
    """
    product_id = request.data.get('product_id')
    user = request.user
    
    if not product_id:
        return Response({'error': 'Thiếu product_id'}, status=400)

    # 1. Tìm tất cả biến thể (variant) của sản phẩm này
    variants = ProductVariant.objects.filter(product_id=product_id)
    
    if not variants.exists():
        return Response({'error': 'Sản phẩm không tồn tại hoặc đã hết hàng'}, status=404)

    # 2. Kiểm tra xem User đã lưu BẤT KỲ biến thể nào của sp này chưa
    existing_item = Wishlist.objects.filter(user=user, variant__in=variants)

    if existing_item.exists():
        # --- TRƯỜNG HỢP XÓA (UNLIKE) ---
        existing_item.delete()
        return Response({'status': 'removed', 'message': 'Đã xóa khỏi danh sách yêu thích'})
    else:
        # --- TRƯỜNG HỢP THÊM (LIKE) ---
        # Lấy biến thể đầu tiên để làm đại diện lưu vào DB
        first_variant = variants.first()
        
        Wishlist.objects.create(
            user=user,
            variant=first_variant
        )
        return Response({'status': 'added', 'message': 'Đã thêm vào danh sách yêu thích'})