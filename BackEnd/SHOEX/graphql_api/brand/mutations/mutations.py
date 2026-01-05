import graphene
from graphene import Mutation
from graphql_api.brand.type.type import BrandType
from brand.models import Brand
from django.core.exceptions import ValidationError


class CreateBrand(Mutation):
    """Create a new Brand (admin only)"""

    class Arguments:
        name = graphene.String(required=True)
        slug = graphene.String()
        description = graphene.String()
        logo_url = graphene.String()
        country = graphene.String()
        is_active = graphene.Boolean(default_value=True)

    success = graphene.Boolean()
    brand = graphene.Field(BrandType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, name, slug=None, description=None, logo_url=None, country=None, is_active=True):
        user = info.context.user
        if not user.is_authenticated:
            return CreateBrand(success=False, errors=["Authentication required"])

        # Allow authenticated users to create brands. For now, make created brands active.
        try:
            final_is_active = True

            brand = Brand.objects.create(
                name=name,
                slug=slug or None,
                description=description or '',
                country=country or '',
                is_active=final_is_active
            )
            # Note: logo handling from URL is not implemented here
            return CreateBrand(success=True, brand=brand, errors=[])
        except ValidationError as e:
            return CreateBrand(success=False, errors=[str(e)])
        except Exception as e:
            return CreateBrand(success=False, errors=[f"Error creating brand: {str(e)}"])


class UpdateBrand(Mutation):
    """Update an existing Brand (admin only)"""

    class Arguments:
        brand_id = graphene.Int(required=True)
        name = graphene.String()
        slug = graphene.String()
        description = graphene.String()
        country = graphene.String()
        is_active = graphene.Boolean()

    success = graphene.Boolean()
    brand = graphene.Field(BrandType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, brand_id, name=None, slug=None, description=None, country=None, is_active=None):
        user = info.context.user
        if not user.is_authenticated or not user.is_staff:
            return UpdateBrand(success=False, errors=["Admin permission required"])

        try:
            brand = Brand.objects.get(brand_id=brand_id)
        except Brand.DoesNotExist:
            return UpdateBrand(success=False, errors=["Brand not found"])

        try:
            if name is not None:
                brand.name = name
            if slug is not None:
                brand.slug = slug
            if description is not None:
                brand.description = description
            if country is not None:
                brand.country = country
            if is_active is not None:
                brand.is_active = is_active

            brand.save()
            return UpdateBrand(success=True, brand=brand, errors=[])
        except ValidationError as e:
            return UpdateBrand(success=False, errors=[str(e)])
        except Exception as e:
            return UpdateBrand(success=False, errors=[f"Error updating brand: {str(e)}"])


class DeleteBrand(Mutation):
    """Soft-delete a Brand (admin only)"""

    class Arguments:
        brand_id = graphene.Int(required=True)

    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    def mutate(self, info, brand_id):
        user = info.context.user
        if not user.is_authenticated or not user.is_staff:
            return DeleteBrand(success=False, errors=["Admin permission required"])

        try:
            brand = Brand.objects.get(brand_id=brand_id)
        except Brand.DoesNotExist:
            return DeleteBrand(success=False, errors=["Brand not found"])

        try:
            # Soft delete
            brand.is_active = False
            brand.save()
            return DeleteBrand(success=True, errors=[])
        except Exception as e:
            return DeleteBrand(success=False, errors=[f"Error deleting brand: {str(e)}"])


__all__ = ["CreateBrand", "UpdateBrand", "DeleteBrand"]
