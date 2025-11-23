import graphene
class ProductSortEnum(graphene.Enum):
    PRICE_ASC = "price_asc"
    PRICE_DESC = "price_desc"
    NAME_ASC = "name_asc"
    NAME_DESC = "name_desc"
    CREATED_AT_DESC = "created_at_desc"
    RATING_DESC = "rating_desc"
    SALES_DESC = "sales_desc"
