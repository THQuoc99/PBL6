from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API trả về danh sách danh mục.
    """
    # Chỉ lấy danh mục cha (parent=None) và đang hoạt động
    queryset = Category.objects.filter(is_active=True, parent__isnull=True)
    serializer_class = CategorySerializer
    permission_classes = [AllowAny] 

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API trả về danh sách sản phẩm.
    """
    # Chỉ lấy sản phẩm đang hoạt động
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    
    # Nếu bạn muốn tìm kiếm theo tên (?search=Nike)
    def get_queryset(self):
        queryset = super().get_queryset()
        search_term = self.request.query_params.get('search', None)
        category_id = self.request.query_params.get('category', None)
        
        if search_term:
            queryset = queryset.filter(name__icontains=search_term)
            
        if category_id:
            queryset = queryset.filter(category__category_id=category_id)
            
        return queryset