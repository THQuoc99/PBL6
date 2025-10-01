import graphene
from graphene import InputObjectType
from django_filters import FilterSet, CharFilter, NumberFilter, BooleanFilter, OrderingFilter
from django.db import models
from django.db.models import Q, Min, Max, Count, F
from products.models import Product, Category, ProductVariant


class ProductFilterSet(FilterSet):
    """
    Django FilterSet cho Product model
    Hỗ trợ filtering backend
    """
    # Tìm kiếm theo tên
    search = CharFilter(method='filter_search')
    
    # Lọc theo danh mục
    category = NumberFilter(field_name='category_id')
    category_in = CharFilter(method='filter_category_in')
    
    # Lọc theo người bán
    seller = NumberFilter(field_name='seller_id')
    seller_name = CharFilter(method='filter_seller_name')
    
    # Lọc theo giá
    price_min = NumberFilter(method='filter_price_min')
    price_max = NumberFilter(method='filter_price_max')
    
    # Lọc theo trạng thái
    is_active = BooleanFilter(field_name='is_active')
    has_stock = BooleanFilter(method='filter_has_stock')
    
    # Lọc theo attributes
    attributes = CharFilter(method='filter_attributes')
    
    # Sắp xếp
    order_by = OrderingFilter(
        fields=(
            ('created_at', 'created_at'),
            ('name', 'name'),
            ('base_price', 'price'),
        )
    )
    
    class Meta:
        model = Product
        fields = ['is_active']
    
    def filter_search(self, queryset, name, value):
        """Tìm kiếm theo tên sản phẩm và mô tả"""
        if not value:
            return queryset
        return queryset.filter(
            Q(name__icontains=value) | 
            Q(description__icontains=value)
        )
    
    def filter_category_in(self, queryset, name, value):
        """Lọc theo nhiều category IDs (phân tách bằng dấu phẩy)"""
        if not value:
            return queryset
        category_ids = [int(id.strip()) for id in value.split(',') if id.strip().isdigit()]
        return queryset.filter(category_id__in=category_ids)
    
    def filter_seller_name(self, queryset, name, value):
        """Lọc theo tên người bán"""
        if not value:
            return queryset
        return queryset.filter(seller__username__icontains=value)
    
    def filter_price_min(self, queryset, name, value):
        """Lọc sản phẩm có giá tối thiểu >= value"""
        if value is None:
            return queryset
        # Lọc products có ít nhất 1 variant có giá >= value
        return queryset.filter(variants__price__gte=value).distinct()
    
    def filter_price_max(self, queryset, name, value):
        """Lọc sản phẩm có giá tối đa <= value"""
        if value is None:
            return queryset
        # Lọc products có ít nhất 1 variant có giá <= value
        return queryset.filter(variants__price__lte=value).distinct()
    
    def filter_has_stock(self, queryset, name, value):
        """Lọc sản phẩm còn hàng"""
        if value:
            return queryset.filter(variants__stock__gt=0).distinct()
        else:
            return queryset.filter(variants__stock=0).distinct()
    
    def filter_attributes(self, queryset, name, value):
        """
        Lọc theo attributes
        Format: "attribute_name:value,attribute_name2:value2"
        VD: "size:38,color:red"
        """
        if not value:
            return queryset
        
        filters = Q()
        for attr_filter in value.split(','):
            if ':' in attr_filter:
                attr_name, attr_value = attr_filter.split(':', 1)
                attr_name = attr_name.strip()
                attr_value = attr_value.strip()
                
                # Lọc products có option với attribute và value tương ứng
                filters &= Q(
                    options__attribute__name__iexact=attr_name,
                    options__value__icontains=attr_value
                )
        
        return queryset.filter(filters).distinct()


# ===== GRAPHQL INPUT TYPES =====

class PriceRangeInput(InputObjectType):
    """Input cho khoảng giá"""
    min_price = graphene.Decimal(description="Giá tối thiểu")
    max_price = graphene.Decimal(description="Giá tối đa")


class AttributeFilterInput(InputObjectType):
    """Input cho lọc theo attributes"""
    attribute_name = graphene.String(required=True, description="Tên thuộc tính")
    values = graphene.List(graphene.String, required=True, description="Danh sách giá trị")


class ProductFilterInput(InputObjectType):
    """
    GraphQL Input cho Product filtering
    Thiết kế theo giao diện Shopee/TikTok
    """
    # ===== TÌM KIẾM =====
    search = graphene.String(description="Từ khóa tìm kiếm")
    
    # ===== DANH MỤC =====
    category_id = graphene.Int(description="ID danh mục")
    category_ids = graphene.List(graphene.Int, description="Danh sách ID danh mục")
    include_subcategories = graphene.Boolean(
        default_value=True, 
        description="Bao gồm danh mục con"
    )
    
    # ===== NGƯỜI BÁN =====
    seller_id = graphene.Int(description="ID người bán")
    seller_name = graphene.String(description="Tên người bán")
    
    # ===== GIÁ CẢ =====
    price_range = graphene.Field(PriceRangeInput, description="Khoảng giá")
    
    # ===== THUỘC TÍNH =====
    attributes = graphene.List(AttributeFilterInput, description="Lọc theo thuộc tính")
    
    # ===== TRẠNG THÁI =====
    is_active = graphene.Boolean(description="Sản phẩm đang hoạt động")
    has_stock = graphene.Boolean(description="Còn hàng")
    has_discount = graphene.Boolean(description="Có giảm giá")
    
    # ===== ĐẶC BIỆT =====
    is_featured = graphene.Boolean(description="Sản phẩm nổi bật")
    is_flash_sale = graphene.Boolean(description="Flash sale")
    
    # ===== RATING =====
    min_rating = graphene.Float(description="Đánh giá tối thiểu")
    
    # ===== SỐ LƯỢNG ĐÃ BÁN =====
    min_sold = graphene.Int(description="Số lượng đã bán tối thiểu")


class ProductSortInput(InputObjectType):
    """
    GraphQL Input cho Product sorting
    Tương tự Shopee/TikTok sorting options
    """
    # Các option sắp xếp phổ biến
    NEWEST = "newest"
    OLDEST = "oldest"
    PRICE_LOW_TO_HIGH = "price_asc"
    PRICE_HIGH_TO_LOW = "price_desc"
    MOST_POPULAR = "popular"
    BEST_SELLING = "best_selling"
    HIGHEST_RATED = "rating_desc"
    
    field = graphene.String(
        required=True,
        description="Trường sắp xếp (newest/oldest/price_asc/price_desc/popular/best_selling/rating_desc)"
    )


class ProductVariantFilterInput(InputObjectType):
    """Input cho ProductVariant filtering"""
    search = graphene.String(description="Tìm kiếm variant")
    product_id = graphene.Int(description="ID sản phẩm")
    price_range = graphene.Field(PriceRangeInput, description="Khoảng giá")
    is_active = graphene.Boolean(description="Variant đang hoạt động")
    has_stock = graphene.Boolean(description="Còn hàng")
    attributes = graphene.List(AttributeFilterInput, description="Lọc theo attributes")


class CategoryFilterInput(InputObjectType):
    """Input cho Category filtering"""
    search = graphene.String(description="Tìm kiếm danh mục")
    parent_id = graphene.Int(description="ID danh mục cha")
    is_active = graphene.Boolean(description="Danh mục đang hoạt động")
    has_products = graphene.Boolean(description="Có sản phẩm")


# ===== HELPER FUNCTIONS =====

def apply_product_filters(queryset, filters):
    """
    Áp dụng filters lên Product queryset
    Được sử dụng trong resolvers
    """
    if not filters:
        return queryset
    
    # Tìm kiếm
    if filters.get('search'):
        search_term = filters['search']
        queryset = queryset.filter(
            Q(name__icontains=search_term) | 
            Q(description__icontains=search_term)
        )
    
    # Danh mục
    if filters.get('category_id'):
        category_id = filters['category_id']
        if filters.get('include_subcategories', True):
            # Bao gồm cả danh mục con
            subcategory_ids = get_subcategory_ids(category_id)
            all_category_ids = [category_id] + subcategory_ids
            queryset = queryset.filter(category_id__in=all_category_ids)
        else:
            queryset = queryset.filter(category_id=category_id)
    
    if filters.get('category_ids'):
        category_ids = filters['category_ids']
        if filters.get('include_subcategories', True):
            # Bao gồm cả danh mục con cho tất cả categories
            all_ids = list(category_ids)
            for cat_id in category_ids:
                all_ids.extend(get_subcategory_ids(cat_id))
            queryset = queryset.filter(category_id__in=all_ids)
        else:
            queryset = queryset.filter(category_id__in=category_ids)
    
    # Người bán
    if filters.get('seller_id'):
        queryset = queryset.filter(seller_id=filters['seller_id'])
    
    if filters.get('seller_name'):
        queryset = queryset.filter(seller__username__icontains=filters['seller_name'])
    
    # Giá cả
    if filters.get('price_range'):
        price_range = filters['price_range']
        if price_range.get('min_price') is not None:
            queryset = queryset.filter(variants__price__gte=price_range['min_price']).distinct()
        if price_range.get('max_price') is not None:
            queryset = queryset.filter(variants__price__lte=price_range['max_price']).distinct()
    
    # Thuộc tính
    if filters.get('attributes'):
        for attr_filter in filters['attributes']:
            attr_name = attr_filter['attribute_name']
            values = attr_filter['values']
            queryset = queryset.filter(
                options__attribute__name__iexact=attr_name,
                options__value__in=values
            ).distinct()
    
    # Trạng thái
    if filters.get('is_active') is not None:
        queryset = queryset.filter(is_active=filters['is_active'])
    
    if filters.get('has_stock') is not None:
        if filters['has_stock']:
            queryset = queryset.filter(variants__stock__gt=0).distinct()
        else:
            queryset = queryset.exclude(variants__stock__gt=0).distinct()
    
    if filters.get('has_discount') is not None:
        if filters['has_discount']:
            # Có ít nhất 1 variant có giá < base_price
            queryset = queryset.filter(variants__price__lt=models.F('base_price')).distinct()
        else:
            # Tất cả variants có giá >= base_price
            queryset = queryset.exclude(variants__price__lt=models.F('base_price')).distinct()
    
    return queryset


def apply_product_sorting(queryset, sort_input):
    """
    Áp dụng sorting lên Product queryset
    """
    if not sort_input or not sort_input.get('field'):
        return queryset.order_by('-created_at')  # Default: newest first
    
    sort_field = sort_input['field']
    
    if sort_field == ProductSortInput.NEWEST:
        return queryset.order_by('-created_at')
    elif sort_field == ProductSortInput.OLDEST:
        return queryset.order_by('created_at')
    elif sort_field == ProductSortInput.PRICE_LOW_TO_HIGH:
        # Sắp xếp theo giá thấp nhất của variants
        return queryset.annotate(
            min_price=Min('variants__price')
        ).order_by('min_price')
    elif sort_field == ProductSortInput.PRICE_HIGH_TO_LOW:
        # Sắp xếp theo giá cao nhất của variants
        return queryset.annotate(
            max_price=Max('variants__price')
        ).order_by('-max_price')
    elif sort_field == ProductSortInput.MOST_POPULAR:
        # TODO: Cần thêm view_count field hoặc popularity metric
        return queryset.order_by('-created_at')
    elif sort_field == ProductSortInput.BEST_SELLING:
        # TODO: Cần tích hợp với order data
        return queryset.order_by('-created_at')
    elif sort_field == ProductSortInput.HIGHEST_RATED:
        # TODO: Cần tích hợp với review data
        return queryset.order_by('-created_at')
    else:
        return queryset.order_by('-created_at')


def get_subcategory_ids(category_id):
    """
    Lấy tất cả subcategory IDs của một category
    Recursive function để lấy all levels
    """
    subcategories = Category.objects.filter(parent_id=category_id, is_active=True)
    subcategory_ids = []
    
    for subcategory in subcategories:
        subcategory_ids.append(subcategory.category_id)
        # Recursive call cho subcategories của subcategory
        subcategory_ids.extend(get_subcategory_ids(subcategory.category_id))
    
    return subcategory_ids


# ===== CATEGORY HELPERS =====

def apply_category_filters(queryset, filters):
    """Áp dụng filters lên Category queryset"""
    if not filters:
        return queryset
    
    if filters.get('search'):
        queryset = queryset.filter(name__icontains=filters['search'])
    
    if filters.get('parent_id') is not None:
        queryset = queryset.filter(parent_id=filters['parent_id'])
    
    if filters.get('is_active') is not None:
        queryset = queryset.filter(is_active=filters['is_active'])
    
    if filters.get('has_products'):
        if filters['has_products']:
            queryset = queryset.filter(products__isnull=False).distinct()
        else:
            queryset = queryset.filter(products__isnull=True)
    
    return queryset