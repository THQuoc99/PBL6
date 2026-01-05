import graphene
class ProductSortInput(graphene.Enum):
    PRICE_ASC = "price_asc"
    PRICE_DESC = "price_desc"
    SALES_DESC = "sales_desc"     # bán chạy (theo tổng sold)
    BEST_SELLING = "best_selling" # bán chạy nhất (30 ngày)
    NEWEST = "newest"             # mới nhất

def apply_product_sorting(qs, sort_key):
    SORT_MAP = {
        "price_asc": "base_price",
        "price_desc": "-base_price",
        "sales_desc": "-sold_count",
        "best_selling": "-sold_count_last_30",
        "newest": "-created_at",
    }
    
    # Convert enum to string value if needed
    if hasattr(sort_key, 'value'):
        sort_key = sort_key.value
    
    print(f"Applying sort: {sort_key}")
    sort_field = SORT_MAP.get(sort_key, "-created_at")
    print(f"Sort field: {sort_field}")
    return qs.order_by(sort_field)
