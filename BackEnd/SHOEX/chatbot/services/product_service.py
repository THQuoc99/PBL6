from products.models import ProductVariant, Category
from django.db.models import Q


def search_products(criteria: dict, limit: int = 5):
    """Search products based on criteria. Returns list of Product objects with display_price."""
    qs = ProductVariant.objects.filter(
        is_active=True,
        stock__gt=0
    ).select_related("product", "product__category")

    # Apply filters only if criteria provided
    has_filter = False
    
    if criteria.get('min_price'):
        qs = qs.filter(price__gte=criteria['min_price'])
        has_filter = True
    if criteria.get('max_price'):
        qs = qs.filter(price__lte=criteria['max_price'])
        has_filter = True

    if criteria.get('color'):
        qs = qs.filter(option_combinations__icontains=criteria['color'])
        has_filter = True
    if criteria.get('size'):
        qs = qs.filter(option_combinations__icontains=f"\"{criteria['size']}\"")
        has_filter = True

    if criteria.get('brand'):
        qs = qs.filter(product__brand__icontains=criteria['brand'])
        has_filter = True
    
    if criteria.get('category'):
        # Tìm category và tất cả subcategories
        categories = Category.objects.filter(
            Q(name__icontains=criteria['category']) | 
            Q(parent__name__icontains=criteria['category'])
        )
        if categories.exists():
            qs = qs.filter(product__category__in=categories)
            has_filter = True
    
    # Keyword search in product name (search with OR condition)
    if criteria.get('keyword'):
        keyword_parts = criteria['keyword'].split()
        q_objects = Q()
        for kw in keyword_parts:
            q_objects |= Q(product__name__icontains=kw)
        qs = qs.filter(q_objects)
        has_filter = True

    sort = criteria.get('sort')
    if sort == 'price_desc':
        qs = qs.order_by('-price')
    elif sort == 'price_asc':
        qs = qs.order_by('price')
    elif sort == 'best_selling':
        # Sắp xếp theo số lượng đã bán (giả sử có field sold_count) hoặc rating
        qs = qs.order_by('-product__review_count', '-product__rating')
    else:
        # Default: Show popular/featured products first, then newest
        qs = qs.order_by('-product__is_featured', '-product__rating', '-created_at')

    # Limit queryset before iterating for performance
    qs = qs[:limit * 3]  # Get more variants to ensure we get enough unique products

    products, seen = [], set()
    for v in qs:
        if v.product_id not in seen:
            v.product.display_price = v.price
            products.append(v.product)
            seen.add(v.product_id)
        if len(products) >= limit:
            break

    return products
