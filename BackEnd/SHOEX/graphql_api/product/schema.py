import graphene
from django.db.models import Q, Exists, OuterRef
from graphene import relay
from promise import Promise

from products.models import Product, ProductVariant, Category
from ..core.types import FilterInputObjectType
from ..core.fields import FilterConnectionField, BaseField
from ..core.connection import create_connection_slice

# Import types
from .types.product import (
    ProductType, 
    ProductVariantType, 
    CategoryType,
    ProductCountableConnection,
    ProductVariantCountableConnection,
    CategoryCountableConnection
)

# Import filters
from .filters.product_filters import (
    ProductFilterInput,
    ProductVariantFilterInput,
    CategoryFilterInput
)

# Import mutations
from .mutations.product_mutations import (
    ProductCreate,
    ProductUpdate,
    ProductDelete,
    ProductVariantCreate,
    ProductVariantUpdate,
    ProductVariantDelete,
    CategoryCreate,
    CategoryUpdate,
    CategoryDelete,
    StockUpdate,
    PriceUpdate
)

# Import bulk mutations
from .bulk_mutations import (
    BulkProductCreate,
    BulkProductUpdate,
    BulkProductVariantCreate,
    BulkStockUpdate,
    BulkPriceUpdate,
    BulkProductStatusUpdate,
    BulkVariantStatusUpdate,
    BulkVariantDelete,
    BulkProductDelete,
    BulkStockTransfer
)

# Import dataloaders
from .dataloaders.product_loaders import (
    CategoryByIdLoader,
    ProductsBySellerLoader,
    ProductVariantsByProductLoader
)


class ProductQueries(graphene.ObjectType):
    """Queries cho products trong SHOEX"""
    
    # === SINGLE OBJECT QUERIES ===
    product = BaseField(
        ProductType,
        id=graphene.Argument(graphene.ID, description="ID của sản phẩm"),
        slug=graphene.Argument(graphene.String, description="Slug của sản phẩm"),
        description="Lấy thông tin một sản phẩm"
    )
    
    product_variant = BaseField(
        ProductVariantType,
        id=graphene.Argument(graphene.ID, description="ID của biến thể"),
        sku=graphene.Argument(graphene.String, description="SKU của biến thể"),
        description="Lấy thông tin một biến thể sản phẩm"
    )
    
    category = BaseField(
        CategoryType,
        id=graphene.Argument(graphene.ID, description="ID của danh mục"),
        slug=graphene.Argument(graphene.String, description="Slug của danh mục"),
        description="Lấy thông tin một danh mục"
    )
    
    # === COLLECTION QUERIES ===
    products = FilterConnectionField(
        ProductType,
        filter=ProductFilterInput(description="Bộ lọc sản phẩm"),
        sort_by=graphene.Argument(
            graphene.String,
            description="Sắp xếp theo: price_asc, price_desc, name_asc, name_desc, created_at_desc, rating_desc, sales_desc"
        ),
        search=graphene.Argument(graphene.String, description="Tìm kiếm theo tên sản phẩm"),
        description="Danh sách tất cả sản phẩm"
    )
    
    product_variants = FilterConnectionField(
        ProductVariantType,
        filter=ProductVariantFilterInput(description="Bộ lọc biến thể"),
        sort_by=graphene.Argument(
            graphene.String,
            description="Sắp xếp theo: price_asc, price_desc, stock_asc, stock_desc, created_at_desc"
        ),
        description="Danh sách tất cả biến thể sản phẩm"
    )
    
    categories = FilterConnectionField(
        CategoryType,
        filter=CategoryFilterInput(description="Bộ lọc danh mục"),
        sort_by=graphene.Argument(
            graphene.String,
            description="Sắp xếp theo: name_asc, name_desc, created_at_desc, product_count_desc"
        ),
        description="Danh sách tất cả danh mục"
    )
    
    # === SPECIAL QUERIES ===
    featured_products = FilterConnectionField(
        ProductType,
        first=graphene.Int(description="Số lượng sản phẩm nổi bật"),
        description="Sản phẩm nổi bật (rating cao, bán chạy)"
    )
    
    products_by_seller = FilterConnectionField(
        ProductType,
        seller_id=graphene.Argument(graphene.ID, required=True, description="ID của seller"),
        filter=ProductFilterInput(description="Bộ lọc sản phẩm"),
        description="Sản phẩm của một seller cụ thể"
    )
    
    products_by_category = FilterConnectionField(
        ProductType,
        category_id=graphene.Argument(graphene.ID, required=True, description="ID của danh mục"),
        filter=ProductFilterInput(description="Bộ lọc sản phẩm"),
        description="Sản phẩm trong một danh mục cụ thể"
    )
    
    # === SEARCH QUERIES ===
    search_products = FilterConnectionField(
        ProductType,
        query=graphene.Argument(graphene.String, required=True, description="Từ khóa tìm kiếm"),
        filter=ProductFilterInput(description="Bộ lọc sản phẩm"),
        description="Tìm kiếm sản phẩm toàn văn"
    )
    
    # === RESOLVERS ===
    
    def resolve_product(self, info, id=None, slug=None):
        """Resolve single product"""
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
    
    def resolve_product_variant(self, info, id=None, sku=None):
        """Resolve single product variant"""
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
    
    def resolve_category(self, info, id=None, slug=None):
        """Resolve single category"""
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
        """Resolve product variants list"""
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
    
    def resolve_categories(self, info, **kwargs):
        """Resolve categories list"""
        qs = Category.objects.filter(is_active=True)
        
        # Apply sorting
        sort_by = kwargs.get('sort_by', 'name_asc')
        if sort_by == 'name_asc':
            qs = qs.order_by('name')
        elif sort_by == 'name_desc':
            qs = qs.order_by('-name')
        elif sort_by == 'created_at_desc':
            qs = qs.order_by('-created_at')
        elif sort_by == 'product_count_desc':
            # Annotate with product count
            qs = qs.annotate(
                product_count=Exists(
                    Product.objects.filter(category=OuterRef('pk'), is_active=True)
                )
            ).order_by('-product_count')
        
        return qs
    
    def resolve_featured_products(self, info, **kwargs):
        """Resolve featured products"""
        first = kwargs.get('first', 20)
        
        # TODO: Implement proper featured logic based on ratings, sales, etc.
        # For now, return newest products
        qs = Product.objects.filter(is_active=True).order_by('-created_at')[:first]
        return qs
    
    def resolve_products_by_seller(self, info, seller_id, **kwargs):
        """Resolve products by seller"""
        qs = Product.objects.filter(
            seller_id=seller_id,
            is_active=True
        ).select_related('category', 'seller')
        
        return qs
    
    def resolve_products_by_category(self, info, category_id, **kwargs):
        """Resolve products by category"""
        qs = Product.objects.filter(
            category_id=category_id,
            is_active=True
        ).select_related('category', 'seller')
        
        return qs
    
    def resolve_search_products(self, info, query, **kwargs):
        """Full-text search products"""
        qs = Product.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query),
            is_active=True
        ).select_related('category', 'seller')
        
        # Boost exact matches
        qs = qs.extra(
            select={
                'name_match': "CASE WHEN name ILIKE %s THEN 1 ELSE 0 END",
            },
            select_params=[f'%{query}%'],
            order_by=['-name_match', '-created_at']
        )
        
        return qs


class ProductMutations(graphene.ObjectType):
    """Mutations cho products trong SHOEX"""
    
    # === PRODUCT MUTATIONS ===
    product_create = ProductCreate.Field()
    product_update = ProductUpdate.Field()
    product_delete = ProductDelete.Field()
    
    # === PRODUCT VARIANT MUTATIONS ===
    product_variant_create = ProductVariantCreate.Field()
    product_variant_update = ProductVariantUpdate.Field()
    product_variant_delete = ProductVariantDelete.Field()
    
    # === CATEGORY MUTATIONS ===
    category_create = CategoryCreate.Field()
    category_update = CategoryUpdate.Field()
    category_delete = CategoryDelete.Field()
    
    # === STOCK & PRICE MUTATIONS ===
    stock_update = StockUpdate.Field()
    price_update = PriceUpdate.Field()
    
    # === BULK MUTATIONS ===
    bulk_product_create = BulkProductCreate.Field()
    bulk_product_update = BulkProductUpdate.Field()
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
