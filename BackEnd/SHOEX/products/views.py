from rest_framework import viewsets, filters
from rest_framework.permissions import AllowAny
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API sản phẩm: Hỗ trợ tìm kiếm & Lọc theo danh mục (bao gồm cả danh mục con)
    """
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter] 
    search_fields = ['name', 'description', 'brand__name', 'category__name', 'model_code']
    
    def get_queryset(self):
        # Chỉ lấy sản phẩm active
        queryset = Product.objects.filter(is_active=True)
        
        # 1. Lọc theo Category (Bao gồm cả sub-categories)
        category_id = self.request.query_params.get('category', None)
        
        if category_id:
            try:
                # Tìm danh mục cha
                parent_category = Category.objects.get(pk=category_id)
                
                # Lấy tất cả danh mục con cháu của nó (nếu có)
                categories_to_filter = [parent_category] + list(parent_category.subcategories.all())
                
                # Lọc sản phẩm thuộc bất kỳ danh mục nào trong list trên
                queryset = queryset.filter(category__in=categories_to_filter)
                
            except Category.DoesNotExist:
                return queryset.none()
        
        # 2. Lọc theo Store (nếu cần)
        store_id = self.request.query_params.get('store_id', None)
        if store_id:
             queryset = queryset.filter(store__store_id=store_id)
            
        return queryset

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API danh sách danh mục sản phẩm.
    Mặc định chỉ trả về các danh mục CHA (parent=None).
    """
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        # Chỉ lấy danh mục gốc (Parent Categories)
        return Category.objects.filter(is_active=True, parent__isnull=True)