from rest_framework import permissions


class IsShopOwner(permissions.BasePermission):
    """
    Permission kiểm tra user có phải là owner của shop liên quan đến return request không
    
    Logic:
    - Return request → Order → OrderItem → Variant → Product → Store
    - Check: Store có trong danh sách stores mà user sở hữu không
    
    TODO: Cần thêm owner field vào Store model hoặc tạo StoreOwner model
    Tạm thời: Check user.is_staff hoặc comment để dev sau implement
    """
    
    def has_object_permission(self, request, view, obj):
        # obj là ReturnRequest
        
        # Admin luôn được phép
        if request.user and request.user.is_staff:
            return True
        
        # TODO: Khi có Store.owner hoặc StoreOwner model:
        # 1. Lấy stores từ return request
        # stores = set()
        # for item in obj.items.all():
        #     store = item.order_item.variant.product.store
        #     stores.add(store)
        # 
        # 2. Check user có phải owner của bất kỳ store nào không
        # for store in stores:
        #     if store.owner == request.user:
        #         return True
        #     # Hoặc nếu có StoreOwner model:
        #     # if StoreOwner.objects.filter(store=store, user=request.user).exists():
        #     #     return True
        # 
        # return False
        
        # Tạm thời: Chỉ cho phép staff (admin)
        # Khi implement Store owner, bỏ comment phần trên và xóa dòng này
        return False


class IsBuyerOrShopOwner(permissions.BasePermission):
    """
    Permission cho phép:
    - Buyer: Người tạo return request
    - Shop Owner: Chủ shop bán sản phẩm trong return request
    """
    
    def has_object_permission(self, request, view, obj):
        # obj là ReturnRequest
        
        # Admin luôn được phép
        if request.user and request.user.is_staff:
            return True
        
        # Buyer có thể xem/sửa return request của mình
        if obj.buyer == request.user:
            return True
        
        # Shop owner - dùng IsShopOwner logic
        shop_permission = IsShopOwner()
        return shop_permission.has_object_permission(request, view, obj)
