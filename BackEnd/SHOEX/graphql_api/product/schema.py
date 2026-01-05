# ===== IMPORTS =====
from .ultis.ultis import get_base_product_queryset
import graphene
from django.db.models import Q, Sum, Avg, F, Case, When, BooleanField, Value, OuterRef, Subquery, FloatField, IntegerField, Count
from django.utils import timezone
from datetime import timedelta
from graphene import relay
from promise import Promise
from django.db.models.functions import Coalesce
# ===== DJANGO MODELS =====
from products.models import Product, ProductVariant, Category, ProductAttribute
from brand.models import Brand
from graphene_django import DjangoConnectionField
from .sort.sorting import ProductSortInput, apply_product_sorting
from orders.models import OrderItem  # giả sử OrderItem có field created_at và variant liên kết ProductVariant
from reviews.models import Review
# ===== GRAPHQL TYPES =====
from .types.product import (
    # Product related types
    ProductType, 
    ProductVariantType,
    ProductCountableConnection,
    ProductVariantCountableConnection,
    CategoryType,
    CategoryCountableConnection
)
from .types.product import ProductAttributeType

# ===== FILTER INPUTS =====
from .filters.product_filters import (
    # Product filters
    # ProductFilterInput,
    ProductVariantFilterInput,
    
    # Category filters
    CategoryFilterInput
)
from .filters.filtering import (
    # Product filters
    ProductFilterInput,
    apply_product_filters)
# ===== MUTATIONS =====
# Product & Variant mutations
from .mutations.product_mutations import (
    ProductDelete,
    StockUpdate,
    PriceUpdate
)
from .mutations.product_mutations import (
    CreateProductFull,
)
from .mutations.product_mutations import (
    UpdateProductFull,
)

# Category mutations
from .mutations.product_mutations import (
    CategoryCreate,
    CategoryUpdate,
    CategoryDelete
)

# Image mutations (Product related)
from .mutations.image_mutations import (
    UploadProductImage,
    UploadAttributeOptionImage,
    DeleteProductImage
)

# Bulk mutations
from .bulk_mutations import (
    # Product bulk operations
    BulkProductCreate,
    BulkProductUpdate,
    BulkProductDelete,
    BulkProductStatusUpdate,
    
    # Variant bulk operations
    BulkProductVariantCreate,
    BulkVariantStatusUpdate,
    BulkVariantDelete,
    
    # Stock & Price bulk operations
    BulkStockUpdate,
    BulkPriceUpdate,
    BulkStockTransfer
)

# ===== DATALOADERS =====

class ProductQueries(graphene.ObjectType):
    """Queries cho products và categories trong SHOEX"""
    
    # ===== CATEGORY QUERIES =====
    # Single category query
    category = graphene.Field(
        CategoryType,
        id=graphene.Argument(graphene.ID, description="ID của danh mục"),
        slug=graphene.Argument(graphene.String, description="Slug của danh mục"),
        description="Lấy thông tin một danh mục cụ thể"
    )
    
    # Category collection query
    categories = graphene.ConnectionField(
        CategoryCountableConnection,
        filter=CategoryFilterInput(description="Bộ lọc danh mục"),
        sortBy=graphene.Argument(
            graphene.String,
            description="Sắp xếp theo: name_asc, name_desc, created_at_desc, product_count_desc"
        ),
        description="Danh sách tất cả danh mục với pagination"
    )

    # Product attribute definitions
    product_attributes = graphene.List(
        ProductAttributeType,
        filter=graphene.Argument(graphene.String, description="Filter by attribute name"),
        description="Danh sách định nghĩa thuộc tính (Size, Color...)"
    )

    # ===== PRODUCT QUERIES =====
    # Single product query
    product = graphene.Field(
        ProductType,
        id=graphene.Argument(graphene.ID, description="ID của sản phẩm"),
        slug=graphene.Argument(graphene.String, description="Slug của sản phẩm"),
        description="Lấy thông tin một sản phẩm cụ thể"
    )
    
    # Product collection query
    products = graphene.ConnectionField(
        ProductCountableConnection,
        filter=ProductFilterInput(description="Bộ lọc sản phẩm"),
        sort_by=graphene.Argument(
            ProductSortInput,
            description="Sắp xếp theo: price_asc, price_desc, name_asc, name_desc, created_at_desc, rating_desc, sales_desc"
        ),
        description="Danh sách tất cả sản phẩm với pagination"
    )
    
    # ===== PRODUCT VARIANT QUERIES =====
    # Single variant query
    product_variant = graphene.Field(
        ProductVariantType,
        id=graphene.Argument(graphene.ID, description="ID của biến thể"),
        sku=graphene.Argument(graphene.String, description="SKU của biến thể"),
        description="Lấy thông tin một biến thể sản phẩm cụ thể"
    )
    
    # Variant collection query
    product_variants = graphene.ConnectionField(
        ProductVariantCountableConnection,
        filter=ProductVariantFilterInput(description="Bộ lọc biến thể"),
        sort_by=graphene.Argument(
            graphene.String,
            description="Sắp xếp theo: price_asc, price_desc, stock_asc, stock_desc, created_at_desc"
        ),
        description="Danh sách tất cả biến thể sản phẩm với pagination"
    )
    
    # ===== SPECIALIZED PRODUCT QUERIES =====
    # Featured products
    featured_products = graphene.ConnectionField(
        ProductCountableConnection,
        first=graphene.Int(description="Số lượng sản phẩm nổi bật"),
        description="Sản phẩm nổi bật (rating cao, bán chạy)"
    )
    
    # Products by seller
    products_by_seller = graphene.ConnectionField(
        ProductCountableConnection,
        seller_id=graphene.Argument(graphene.ID, required=True, description="ID của seller"),
        filter=ProductFilterInput(description="Bộ lọc sản phẩm"),
        description="Sản phẩm của một seller cụ thể"
    )
    
    # Products by category
    products_by_category = graphene.ConnectionField(
        ProductCountableConnection,
        category_id=graphene.Argument(graphene.ID, required=True, description="ID của danh mục"),
        filter=ProductFilterInput(description="Bộ lọc sản phẩm"),
        description="Sản phẩm trong một danh mục cụ thể"
    )
    
    # ===== SEARCH QUERIES =====
    # Full-text product search
    search_products = graphene.ConnectionField(
        ProductCountableConnection,
        query=graphene.Argument(graphene.String, required=True, description="Từ khóa tìm kiếm"),
        filter=ProductFilterInput(description="Bộ lọc sản phẩm"),
        description="Tìm kiếm sản phẩm toàn văn"
    )
    
    # ===== CATEGORY RESOLVERS =====
    
    def resolve_category(self, info, id=None, slug=None):
        """Resolve single category by ID or slug"""
        if id:
            try:
                return Category.objects.get(category_id=id, is_active=True)
            except Category.DoesNotExist:
                return None
        elif slug:
            try:
                return Category.objects.get(slug=slug, is_active=True)
            except Category.DoesNotExist:
                return None
        return None
    

    def resolve_categories(self, info, **kwargs):
        """Resolve categories list with filtering and sorting"""
        qs = Category.objects.all()

        # --- 1️⃣ Lọc theo filter ---
        filter_data = kwargs.get('filter', {})
        if filter_data:
            if 'isActive' in filter_data:
                qs = qs.filter(is_active=filter_data['isActive'])
            if 'parentId' in filter_data:
                # parentId = None → danh mục gốc
                parent_id = filter_data['parentId']
                if parent_id is None:
                    qs = qs.filter(parent__isnull=True)
                else:
                    qs = qs.filter(parent_id=parent_id)
            if 'search' in filter_data:
                qs = qs.filter(name__icontains=filter_data['search'])
            if 'hasProducts' in filter_data and filter_data['hasProducts']:
                qs = qs.annotate(product_count=Count('products')).filter(product_count__gt=0)

        # --- 2️⃣ Sắp xếp (sort) ---
        sort_by = kwargs.get('sortBy', 'name_asc')
        if sort_by == 'name_asc':
            qs = qs.order_by('name')
        elif sort_by == 'name_desc':
            qs = qs.order_by('-name')
        elif sort_by == 'created_at_desc':
            qs = qs.order_by('-created_at')
        elif sort_by == 'product_count_desc':
            qs = qs.annotate(product_count=Count('products')).order_by('-product_count')

        return qs

    def resolve_product_attributes(self, info, filter=None):
        """Trả về danh sách ProductAttribute (có thể lọc theo tên)"""
        qs = ProductAttribute.objects.all()
        if filter:
            qs = qs.filter(name__icontains=filter)
        return qs

    
    # ===== PRODUCT RESOLVERS =====
    
    def resolve_product(self, info, id=None, slug=None):
        """Resolve single product by ID or slug, lấy từ qs base annotate"""
        qs = get_base_product_queryset()
        if id:
            try:
                return qs.get(product_id=id)
            except Product.DoesNotExist:
                return None
        elif slug:
            try:
                return qs.get(slug=slug)
            except Product.DoesNotExist:
                return None
        return None
    
    # ===== PRODUCT VARIANT RESOLVERS =====
    
    def resolve_product_variant(self, info, id=None, sku=None):
        """Resolve single product variant by ID or SKU"""
        if id:
            try:
                return ProductVariant.objects.get(variant_id=id, is_active=True)
            except ProductVariant.DoesNotExist:
                return None
        elif sku:
            try:
                return ProductVariant.objects.get(sku=sku, is_active=True)
            except ProductVariant.DoesNotExist:
                return None
        return None

    def resolve_products(self, info, **kwargs):
        """Resolve danh sách Product với filter và sort"""
        qs = get_base_product_queryset()

        # Apply filtering (sử dụng helper)
        filter_data = kwargs.get("filter")
        if filter_data:
            qs = apply_product_filters(qs, filter_data)

        # Apply sorting (sử dụng helper)
        sort_by = kwargs.get('sort_by', 'created_at_desc')
        qs = apply_product_sorting(qs, sort_by)

        # Debug: In ra 3 sản phẩm đầu để kiểm tra sort
        import logging
        logger = logging.getLogger(__name__)
        for i, p in enumerate(qs[:3]):
            logger.info(f"Product {i}: ID={p.product_id}, variant_min_price={getattr(p, 'variant_min_price', 'N/A')}, base_price={p.base_price}")

        return qs
    
    def resolve_product_variants(self, info, **kwargs):
        """Resolve product variants list with filtering and sorting"""
        qs = ProductVariant.objects.filter(is_active=True).select_related('product')
        
        # Apply sorting
        sort_by = kwargs.get('sort_by', 'created_at_desc')
        if sort_by == 'price_asc':
            qs = qs.order_by('price')
        elif sort_by == 'price_desc':
            qs = qs.order_by('-price')
        elif sort_by == 'stock_asc':
            qs = qs.order_by('stock')
        elif sort_by == 'stock_desc':
            qs = qs.order_by('-stock')
        elif sort_by == 'created_at_desc':
            qs = qs.order_by('-created_at')
        
        return qs
    
    # ===== SPECIALIZED PRODUCT RESOLVERS =====
    
    def resolve_featured_products(self, info, **kwargs):
        """Resolve featured products based on ratings and sales"""
        first = kwargs.get('first', 20)
        
        # TODO: Implement proper featured logic based on ratings, sales, etc.
        # For now, return newest products
        qs = Product.objects.filter(is_active=True).order_by('-created_at')[:first]
        return qs
    
    def resolve_products_by_seller(self, info, seller_id, **kwargs):
        """Resolve products by specific seller"""
        qs = Product.objects.filter(
            store_id=seller_id,
            is_active=True
        ).select_related('category', 'store')
        
        return qs
    
    def resolve_products_by_category(self, info, category_id, **kwargs):
        """Resolve products by specific category"""
        qs = Product.objects.filter(
            category_id=category_id,
            is_active=True
        ).select_related('category', 'store')
        
        return qs
    
    # ===== SEARCH RESOLVERS =====
    
    def resolve_search_products(self, info, query, **kwargs):
        """Full-text search products with relevance ranking"""
        qs = Product.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query),
            is_active=True
        ).select_related('category', 'store')
        
        # Boost exact matches for better relevance
        qs = qs.extra(
            select={
                'name_match': "CASE WHEN name ILIKE %s THEN 1 ELSE 0 END",
            },
            select_params=[f'%{query}%'],
            order_by=['-name_match', '-created_at']
        )
        
        return qs


class ProductMutations(graphene.ObjectType):
    """Mutations cho products và categories trong SHOEX"""
    
    # ===== CATEGORY MUTATIONS =====
    # Category CRUD operations
    category_create = CategoryCreate.Field()
    category_update = CategoryUpdate.Field()
    category_delete = CategoryDelete.Field()

    
    # ===== STOCK & PRICE MUTATIONS =====
    # Inventory and pricing operations
    stock_update = StockUpdate.Field()
    price_update = PriceUpdate.Field()
    
    # ===== FULL PRODUCT MUTATION =====
    # Full product creation (with uploads)
    create_product_full = CreateProductFull.Field()
    update_product_full = UpdateProductFull.Field()
    
    # ===== IMAGE MUTATIONS =====
    # Image upload and management operations
    upload_product_image = UploadProductImage.Field()
    upload_attribute_option_image = UploadAttributeOptionImage.Field()
    delete_product_image = DeleteProductImage.Field()
    
    # ===== BULK OPERATIONS =====
    # Bulk product operations
    bulk_product_create = BulkProductCreate.Field()
    bulk_product_update = BulkProductUpdate.Field()
    bulk_product_delete = BulkProductDelete.Field()
    bulk_product_status_update = BulkProductStatusUpdate.Field()
    
    # Bulk variant operations
    bulk_product_variant_create = BulkProductVariantCreate.Field()
    bulk_variant_status_update = BulkVariantStatusUpdate.Field()
    bulk_variant_delete = BulkVariantDelete.Field()
    
    # Bulk stock & price operations
    bulk_stock_update = BulkStockUpdate.Field()
    bulk_price_update = BulkPriceUpdate.Field()
    bulk_stock_transfer = BulkStockTransfer.Field()
    bulk_product_variant_create = BulkProductVariantCreate.Field()
    bulk_stock_update = BulkStockUpdate.Field()
    bulk_price_update = BulkPriceUpdate.Field()
    bulk_product_status_update = BulkProductStatusUpdate.Field()
    bulk_variant_status_update = BulkVariantStatusUpdate.Field()
    bulk_variant_delete = BulkVariantDelete.Field()
    bulk_product_delete = BulkProductDelete.Field()
    bulk_stock_transfer = BulkStockTransfer.Field()



# Export for schema integration
__all__ = [
    'ProductQueries',
    'ProductMutations'
]

ProductQuery = ProductQueries
ProductMutation = ProductMutations

# Đảm bảo export đúng tên
ProductQuery = ProductQuery
ProductMutation = ProductMutation
