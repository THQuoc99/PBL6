import graphene
from graphene_file_upload.scalars import Upload


class ProductImageInput(graphene.InputObjectType):
    image = Upload(required=True)
    isThumbnail = graphene.Boolean(default_value=False)
    altText = graphene.String()
    displayOrder = graphene.Int(default_value=0)


class AttributeOptionInput(graphene.InputObjectType):
    attributeId = graphene.ID(required=True)
    value = graphene.String(required=True)
    valueCode = graphene.String()
    image = Upload()
    displayOrder = graphene.Int(default_value=0)


class VariantInput(graphene.InputObjectType):
    sku = graphene.String()
    price = graphene.Float(required=True)
    stock = graphene.Int(required=True)
    optionCombinations = graphene.JSONString(required=True)


class CreateProductFullInput(graphene.InputObjectType):
    storeId = graphene.ID(required=True)
    categoryId = graphene.ID(required=True)
    name = graphene.String(required=True)
    slug = graphene.String()
    description = graphene.String(required=True)
    basePrice = graphene.Float(required=True)
    brandId = graphene.ID()
    isFeatured = graphene.Boolean()
    isActive = graphene.Boolean(default_value=True)
    sizeGuideImage = Upload()
    images = graphene.List(ProductImageInput)
    attributeOptions = graphene.List(AttributeOptionInput)
    variants = graphene.List(VariantInput)
