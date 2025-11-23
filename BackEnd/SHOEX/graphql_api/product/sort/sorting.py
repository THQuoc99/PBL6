import graphene
class ProductSortInput(graphene.Enum):
    PRICE_ASC = "price_asc"
    PRICE_DESC = "price_desc"
    NAME_ASC = "name_asc"
    NAME_DESC = "name_desc"
    CREATED_AT_DESC = "created_at_desc"
    RATING_DESC = "rating_desc"
    SALES_DESC = "sales_desc"     # bán chạy (theo tổng sold)
    BEST_SELLING = "best_selling" # bán chạy nhất (30 ngày)
    NEWEST = "newest"             # mới nhất

def apply_product_sorting(qs, sort_key):
    SORT_MAP = {
        "price_asc": "base_price",
        "price_desc": "-base_price",
        "name_asc": "name",
        "name_desc": "-name",
        "created_at_desc": "-created_at",
        "rating_desc": "-avg_rating_last_30",
        "sales_desc": "-sold_count",
        "best_selling": "-sold_count_last_30",
        "newest": "-created_at",
    }

    sort_field = SORT_MAP.get(sort_key, "-created_at")
    return qs.order_by(sort_field)
