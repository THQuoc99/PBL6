from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from .models import Store, StoreFollower
from .serializers import StoreSerializer

class StoreViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API:
    - GET /api/store/ : Danh sách cửa hàng
    - GET /api/store/{id}/ : Chi tiết cửa hàng
    - POST /api/store/{id}/follow/ : Theo dõi/Hủy theo dõi
    """
    queryset = Store.objects.filter(is_active=True)
    serializer_class = StoreSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']
    lookup_field = 'store_id' # URL sẽ dùng store_id (VD: SHOP-001) thay vì id số

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def follow(self, request, store_id=None):
        store = self.get_object()
        user = request.user
        
        follower, created = StoreFollower.objects.get_or_create(store=store, user=user)
        
        if not created:
            # Nếu đã tồn tại -> Xóa (Unfollow) hoặc Toggle trạng thái
            follower.delete()
            store.followers_count = max(0, store.followers_count - 1)
            store.save()
            return Response({'status': 'unfollowed', 'message': 'Đã hủy theo dõi shop'})
        
        # Nếu mới tạo -> Follow
        store.followers_count += 1
        store.save()
        return Response({'status': 'followed', 'message': 'Đã theo dõi shop'})