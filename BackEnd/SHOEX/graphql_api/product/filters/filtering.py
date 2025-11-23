import graphene
from graphene import InputObjectType
from django.db.models import Q, Sum, Avg, F, Case, When, Value, BooleanField
from django.db.models.functions import Coalesce
from products.models import Product, Category
from django.utils import timezone
from datetime import timedelta

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
    store_id = graphene.Int(description="ID người bán")
    store_name = graphene.String(description="Tên người bán")
    
    # ===== GIÁ CẢ =====
    price_range = graphene.Field(PriceRangeInput, description="Khoảng giá")
    
    # ===== THUỘC TÍNH =====
    attributes = graphene.List(AttributeFilterInput, description="Lọc theo thuộc tính")
    
    # ===== TRẠNG THÁI =====
    has_stock = graphene.Boolean(description="Còn hàng")
    has_discount = graphene.Boolean(description="Có giảm giá")
    
    # ===== ĐẶC BIỆT =====
    is_hot = graphene.Boolean(description="Sản phẩm bán chạy")
    is_flash_sale = graphene.Boolean(description="Flash sale")
    is_new = graphene.Boolean(description="Sản phầm mới")
    
    # ===== RATING =====
    min_rating = graphene.Float(description="Đánh giá tối thiểu")
    
    # ===== SỐ LƯỢNG ĐÃ BÁN =====
    min_sold = graphene.Int(description="Số lượng đã bán tối thiểu")




    # ===== GET SUBCATEGORY IDS =====
def get_subcategory_ids(category_id):
    subcategories = Category.objects.filter(parent_id=category_id, is_active=True)
    ids = []
    for sub in subcategories:
        ids.append(sub.category_id)
        ids.extend(get_subcategory_ids(sub.category_id))
    return ids

# ===== APPLY PRODUCT FILTERS =====
def apply_product_filters(queryset, filters):
    if not filters:
        return queryset

    if getattr(filters, "search", None):
        queryset = queryset.filter(Q(name__icontains=filters.search) |
                                   Q(description__icontains=filters.search))

    if getattr(filters, "category_id", None):
        cat_id = filters.category_id
        if getattr(filters, "include_subcategories", True):
            all_ids = [cat_id] + get_subcategory_ids(cat_id)
            queryset = queryset.filter(category_id__in=all_ids)
        else:
            queryset = queryset.filter(category_id=cat_id)

    if getattr(filters, "category_ids", None):
        ids = []
        for cid in filters.category_ids:
            ids.append(cid)
            if getattr(filters, "include_subcategories", True):
                ids.extend(get_subcategory_ids(cid))
        queryset = queryset.filter(category_id__in=ids)

    if getattr(filters, "store_id", None):
        queryset = queryset.filter(store_id=filters.store_id)
    if getattr(filters, "store_name", None):
        queryset = queryset.filter(store__name__icontains=filters.store_name)

    if getattr(filters, "price_range", None):
        pr = filters.price_range
        if pr.min_price is not None:
            queryset = queryset.filter(base_price__gte=pr.min_price)
        if pr.max_price is not None:
            queryset = queryset.filter(base_price__lte=pr.max_price)

    if getattr(filters, "has_stock", None) is not None:
        if filters.has_stock:
            queryset = queryset.filter(variants__stock__gt=0).distinct()
        else:
            queryset = queryset.exclude(variants__stock__gt=0).distinct()

    if getattr(filters, "has_discount", None):
        if filters.has_discount:
            queryset = queryset.filter(variants__price__lt=F('base_price')).distinct()

    if getattr(filters, "is_hot", None):
        if filters.is_hot:
            queryset = queryset.filter(is_hot=True)

    if getattr(filters, "is_new", None):
        if filters.is_new:
            queryset = queryset.filter(is_new=True)

    if getattr(filters, "min_rating", None):
        queryset = queryset.filter(avg_rating_last_30__gte=filters.min_rating)

    if getattr(filters, "min_sold", None):
        queryset = queryset.filter(sold_count_last_30__gte=filters.min_sold)

    return queryset