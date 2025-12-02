from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Review, ReviewHelpful
from .serializers import ReviewSerializer, CreateReviewSerializer
from products.models import Product

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    
    # Cho phép lọc theo rating
    filterset_fields = ['rating']
    ordering_fields = ['created_at', 'rating']

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateReviewSerializer
        return ReviewSerializer

    def get_queryset(self):
        """
        Lọc review theo sản phẩm (product_id)
        URL: /api/reviews/?product_id=1
        """
        queryset = super().get_queryset()
        product_id = self.request.query_params.get('product_id')
        
        if product_id:
            # Truy vấn ngược từ Review -> OrderItem -> Variant -> Product
            queryset = queryset.filter(order_item__variant__product_id=product_id)
            
        return queryset

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def vote_helpful(self, request, pk=None):
        """Toggle vote hữu ích"""
        review = self.get_object()
        user = request.user
        
        vote, created = ReviewHelpful.objects.get_or_create(review=review, user=user)
        
        if not created:
            # Nếu đã vote rồi thì xóa (Unvote)
            vote.delete()
            return Response({'status': 'unvoted', 'message': 'Đã bỏ bình chọn'})
        
        return Response({'status': 'voted', 'message': 'Đã bình chọn hữu ích'})