import graphene
from graphql_api.brand.type.type import BrandType
from brand.models import Brand


class BrandQuery(graphene.ObjectType):
    """Brand queries"""

    brand = graphene.Field(
        BrandType,
        brand_id=graphene.Argument(graphene.Int, description="ID của thương hiệu"),
        slug=graphene.Argument(graphene.String, description="Slug của thương hiệu")
    )

    brands = graphene.List(
        BrandType,
        is_active=graphene.Argument(graphene.Boolean, description="Lọc theo trạng thái active"),
        description="Danh sách thương hiệu"
    )

    def resolve_brand(self, info, brand_id=None, slug=None):
        if brand_id:
            try:
                return Brand.objects.get(brand_id=brand_id)
            except Brand.DoesNotExist:
                return None
        if slug:
            try:
                return Brand.objects.get(slug=slug)
            except Brand.DoesNotExist:
                return None
        return None

    def resolve_brands(self, info, is_active=None):
        qs = Brand.objects.all()
        if is_active is not None:
            qs = qs.filter(is_active=is_active)
        return qs.order_by('name')


class BrandMutations(graphene.ObjectType):
    from .mutations.mutations import (
        CreateBrand,
        UpdateBrand,
        DeleteBrand
    )

    create_brand = CreateBrand.Field()
    update_brand = UpdateBrand.Field()
    delete_brand = DeleteBrand.Field()


__all__ = ["BrandQuery", "BrandMutations"]
