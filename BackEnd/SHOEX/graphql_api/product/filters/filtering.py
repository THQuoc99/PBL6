import graphene
from graphene import InputObjectType
from django.db.models import Q, Sum, Avg, F, Case, When, Value, BooleanField
from django.db.models.functions import Coalesce
from products.models import Product, Category
from django.utils import timezone
from django.utils.timezone import make_aware, is_naive
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

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
    brand_id = graphene.Int(description="thương hiệu ")
    store_id = graphene.ID(description="cửa hàng ")
    # ===== GIÁ CẢ =====
    price_range = graphene.Field(PriceRangeInput, description="Khoảng giá")
    
    # ===== THUỘC TÍNH =====

    # ===== TRẠNG THÁI =====
    has_stock = graphene.Boolean(description="Còn hàng")
    has_discount = graphene.Boolean(description="Có giảm giá")
    
    # ===== ĐẶC BIỆT =====
    is_hot = graphene.Boolean(description="Sản phẩm bán chạy")
    is_new = graphene.Boolean(description="Sản phầm mới")
    
    # ===== RATING =====
    min_rating = graphene.Float(description="Đánh giá tối thiểu")
    
    # ===== SỐ LƯỢNG ĐÃ BÁN =====
    min_sold = graphene.Int(description="Số lượng đã bán tối thiểu")

        # ===== THỜI GIAN TẠO =====
    created_today = graphene.Boolean(description="Sản phẩm tạo hôm nay")
    created_this_week = graphene.Boolean(description="Sản phẩm tạo trong tuần này")
    created_this_month = graphene.Boolean(description="Sản phẩm tạo trong tháng này")
    # ===== CREATED AT RANGE =====
    created_from = graphene.DateTime(description="Sản phẩm tạo từ (ISO datetime)")
    created_to = graphene.DateTime(description="Sản phẩm tạo đến (ISO datetime)")




    # ===== GET SUBCATEGORY IDS =====
def get_subcategory_ids(category_id):
    subcategories = Category.objects.filter(parent_id=category_id, is_active=True)
    ids = []
    for sub in subcategories:
        ids.append(sub.category_id)
        ids.extend(get_subcategory_ids(sub.category_id))
    return ids

# ===== APPLY PRODUCT FILTERS =====
# TẠM THỜI BỎ QUA CÁC TRƯỜNG THIẾU TRONG ProductFilterInput (store_id, store_name)
# VÌ CHÚNG KHÔNG CÓ TRONG INPUT OBJECT BẠN CUNG CẤP.

def apply_product_filters(queryset, filters):
    """
    Áp dụng các điều kiện lọc sản phẩm dựa trên input GraphQL.
    """
    if not filters:
        return queryset

    # Debug: log incoming filter fields to help diagnose mismatches
    try:
        debug_payload = {
            'search': getattr(filters, 'search', None),
            'category_id': getattr(filters, 'category_id', None),
            'category_ids': getattr(filters, 'category_ids', None),
            'store_id': getattr(filters, 'store_id', None),
            'price_range': getattr(filters, 'price_range', None),
            'is_new': getattr(filters, 'is_new', None),
            'created_today': getattr(filters, 'created_today', None),
            'created_this_week': getattr(filters, 'created_this_week', None),
            'created_this_month': getattr(filters, 'created_this_month', None),
            'created_from': getattr(filters, 'created_from', None),
            'created_to': getattr(filters, 'created_to', None),
        }
        logger.debug('apply_product_filters input: %s', debug_payload)
    except Exception:
        logger.debug('apply_product_filters received filters (unable to enumerate)')
    print('Applying product filters:', filters)
    # ===== TÌM KIẾM (Search) =====
    if getattr(filters, "search", None):
        queryset = queryset.filter(Q(name__icontains=filters.search) |
                                   Q(description__icontains=filters.search))

    # ===== DANH MỤC (Category) =====
    
    # Lọc theo một category_id
    if getattr(filters, "category_id", None):
        cat_id = filters.category_id
        if getattr(filters, "include_subcategories", True):
            # Lấy tất cả ID danh mục con (sử dụng đệ quy)
            all_ids = [cat_id] + get_subcategory_ids(cat_id)
            queryset = queryset.filter(category_id__in=all_ids)
        else:
            queryset = queryset.filter(category_id=cat_id)

    # Lọc theo danh sách category_ids
    if getattr(filters, "category_ids", None):
        ids = []
        for cid in filters.category_ids:
            ids.append(cid)
            if getattr(filters, "include_subcategories", True):
                ids.extend(get_subcategory_ids(cid))
        queryset = queryset.filter(category_id__in=ids)

    # ===== NGƯỜI BÁN (Brand) =====
    if getattr(filters, "brand_id", None):
        queryset = queryset.filter(brand_id=filters.brand_id)

    if getattr(filters, "store_id", None):
        try:
            logger.debug('apply_product_filters - store_id incoming type=%s value=%s', type(filters.store_id), filters.store_id)
        except Exception:
            logger.debug('apply_product_filters - store_id present (unable to inspect)')
        before_count = queryset.count()
        queryset = queryset.filter(store_id=filters.store_id)
        after_count = queryset.count()
        logger.debug('apply_product_filters - applied store_id filter: before=%s after=%s', before_count, after_count)

    # ===== GIÁ CẢ (Price Range) =====
    # Dùng base_price hoặc giá bán (price) tùy theo logic kinh doanh. 
    # Nếu dùng base_price thì phải đảm bảo base_price đã được annotation hoặc là trường trực tiếp.
    # Trong ví dụ này, tôi dùng trường 'price' của variants (nếu có) hoặc base_price (nếu có). 
    # Giả sử chúng ta lọc trên giá bán cuối cùng (có thể là price của variant, hoặc base_price nếu không có variant).
    # Tuy nhiên, dựa trên code cũ của bạn (base_price), tôi sẽ giữ nguyên lọc trên base_price:
    
    if getattr(filters, "price_range", None):
        pr = filters.price_range
        # Lọc giá tối thiểu
        if pr.min_price is not None:
            # Giả sử lọc trên giá cơ bản (base_price)
            queryset = queryset.filter(base_price__gte=pr.min_price)
        # Lọc giá tối đa
        if pr.max_price is not None:
            # Giả sử lọc trên giá cơ bản (base_price)
            queryset = queryset.filter(base_price__lte=pr.max_price)

    # ===== TRẠNG THÁI (Stock & Discount) =====

    # Còn hàng (has_stock)
    if getattr(filters, "has_stock", None) is not None:
        if filters.has_stock:
            # Lọc sản phẩm có ít nhất một variant còn hàng
            queryset = queryset.filter(variants__stock__gt=0).distinct()
        else:
            # Lọc sản phẩm KHÔNG có variant nào còn hàng
            queryset = queryset.exclude(variants__stock__gt=0).distinct()

    # Có giảm giá (has_discount)
    if getattr(filters, "has_discount", None):
        if filters.has_discount:
            # Lọc sản phẩm có ít nhất một variant có giá bán (price) thấp hơn giá gốc (base_price)
            # Yêu cầu trường 'base_price' phải có sẵn
            queryset = queryset.filter(variants__price__lt=F('base_price')).distinct()

    # ===== ĐẶC BIỆT (Hot & New) =====
    
    # Sản phẩm bán chạy (is_hot)
    # Giả định có trường is_hot trên mô hình Product
    if getattr(filters, "is_hot", None):
        if filters.is_hot:
            queryset = queryset.filter(is_hot=True)

    # Sản phẩm mới (is_new)
    # Giả định có trường is_new trên mô hình Product
    if getattr(filters, "is_new", None):
        if filters.is_new:
            queryset = queryset.filter(is_new=True)

    # ===== ĐÁNH GIÁ (Rating) =====
    # Yêu cầu Product QuerySet phải được annotate với 'avg_rating' trước đó.
    if getattr(filters, "min_rating", None):
        queryset = queryset.filter(avg_rating__gte=filters.min_rating)

    # ===== SỐ LƯỢNG ĐÃ BÁN (Sold Count) =====
    # Yêu cầu Product QuerySet phải được annotate với 'sold_count_last_30' trước đó.
    # Lưu ý: Tôi đang giả định 'min_sold' áp dụng cho sold_count_last_30 như trong code cũ.
    if getattr(filters, "min_sold", None):
        queryset = queryset.filter(sold_count_last_30__gte=filters.min_sold)

    # ===== THỜI GIAN TẠO (created_at) =====
    # Support explicit datetime range filters (`created_from`/`created_to`).
    # If either `created_from` or `created_to` is provided, those take precedence
    # over the convenience boolean flags (`created_today`, `created_this_week`, `created_this_month`).
    has_from = getattr(filters, 'created_from', None) is not None
    has_to = getattr(filters, 'created_to', None) is not None

    if has_from or has_to:
        if has_from:
            start = filters.created_from
            if is_naive(start):
                start = make_aware(start, timezone.get_current_timezone())
            queryset = queryset.filter(created_at__gte=start)
        if has_to:
            end = filters.created_to
            if is_naive(end):
                end = make_aware(end, timezone.get_current_timezone())
            queryset = queryset.filter(created_at__lte=end)
    else:
        # Filter products created today / this week / this month (convenience booleans)
        if getattr(filters, 'created_today', None):
            start_day = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
            queryset = queryset.filter(created_at__gte=start_day)

        if getattr(filters, 'created_this_week', None):
            today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
            # ISO weekday: Monday=0
            start_week = today - timedelta(days=today.weekday())
            queryset = queryset.filter(created_at__gte=start_week)

        if getattr(filters, 'created_this_month', None):
            now = timezone.now()
            start_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            queryset = queryset.filter(created_at__gte=start_month)

    return queryset