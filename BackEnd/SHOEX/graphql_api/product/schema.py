# ===== IMPORTS =====
import graphene
from django.db.models import Q, Exists, OuterRef, Count
from graphene import relay
from promise import Promise
from django.db.models import Count, Q

# ===== DJANGO MODELS =====
from products.models import Product, ProductVariant, Category
from graphene_django import DjangoConnectionField

# ===== GRAPHQL TYPES =====
from .types.product import (
    # Product related types
    ProductType, 
    ProductVariantType,
    ProductCountableConnection,
    ProductVariantCountableConnection,
    
    # Category related types
    CategoryType,
    CategoryCountableConnection
)

# ===== FILTER INPUTS =====
from .filters.product_filters import (
    # Product filters
    ProductFilterInput,
    ProductVariantFilterInput,
    
    # Category filters
    CategoryFilterInput
)

# ===== MUTATIONS =====
# Product & Variant mutations
from .mutations.product_mutations import (
    ProductCreate,
    ProductUpdate,
    ProductDelete,
    ProductVariantCreate,
    ProductVariantUpdate,
    ProductVariantDelete,
    StockUpdate,
    PriceUpdate
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
            graphene.String,
            description="Sắp xếp theo: price_asc, price_desc, name_asc, name_desc, created_at_desc, rating_desc, sales_desc"
        ),
        search=graphene.Argument(graphene.String, description="Tìm kiếm theo tên sản phẩm"),
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

    
    # ===== PRODUCT RESOLVERS =====
    
    def resolve_product(self, info, id=None, slug=None):
        """Resolve single product by ID or slug"""
        if id:
            try:
                return Product.objects.get(product_id=id, is_active=True)
            except Product.DoesNotExist:
                return None
        elif slug:
            try:
                return Product.objects.get(slug=slug, is_active=True)
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
        """Resolve products list with filtering and sorting"""
        qs = Product.objects.filter(is_active=True).select_related('category', 'seller')
        
        # Apply search
        search = kwargs.get('search')
        if search:
            qs = qs.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search)
            )
        
        # Apply sorting
        sort_by = kwargs.get('sort_by', 'created_at_desc')
        if sort_by == 'price_asc':
            qs = qs.order_by('base_price')
        elif sort_by == 'price_desc':
            qs = qs.order_by('-base_price')
        elif sort_by == 'name_asc':
            qs = qs.order_by('name')
        elif sort_by == 'name_desc':
            qs = qs.order_by('-name')
        elif sort_by == 'created_at_desc':
            qs = qs.order_by('-created_at')
        elif sort_by == 'rating_desc':
            # TODO: Add rating sorting when reviews are implemented
            qs = qs.order_by('-created_at')
        elif sort_by == 'sales_desc':
            # TODO: Add sales sorting when orders are implemented
            qs = qs.order_by('-created_at')
        
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
            seller_id=seller_id,
            is_active=True
        ).select_related('category', 'seller')
        
        return qs
    
    def resolve_products_by_category(self, info, category_id, **kwargs):
        """Resolve products by specific category"""
        qs = Product.objects.filter(
            category_id=category_id,
            is_active=True
        ).select_related('category', 'seller')
        
        return qs
    
    # ===== SEARCH RESOLVERS =====
    
    def resolve_search_products(self, info, query, **kwargs):
        """Full-text search products with relevance ranking"""
        qs = Product.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query),
            is_active=True
        ).select_related('category', 'seller')
        
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
    
    # ===== PRODUCT MUTATIONS =====
    # Product CRUD operations
    product_create = ProductCreate.Field()
    product_update = ProductUpdate.Field()
    product_delete = ProductDelete.Field()
    
    # ===== PRODUCT VARIANT MUTATIONS =====
    # Product variant CRUD operations
    product_variant_create = ProductVariantCreate.Field()
    product_variant_update = ProductVariantUpdate.Field()
    product_variant_delete = ProductVariantDelete.Field()
    
    # ===== STOCK & PRICE MUTATIONS =====
    # Inventory and pricing operations
    stock_update = StockUpdate.Field()
    price_update = PriceUpdate.Field()
    
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

# Đảm bảo tên export đúng để import từ api.py
# Đổi tên class nếu cần, hoặc thêm alias cuối file
ProductQuery = ProductQueries
ProductMutation = ProductMutations

# Đảm bảo export đúng tên
ProductQuery = ProductQuery
ProductMutation = ProductMutation
