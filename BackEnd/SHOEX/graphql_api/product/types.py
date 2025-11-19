import graphene
from graphene_django import DjangoObjectType
from products.models import (
    Product, Category, ProductVariant, ProductImage,
    ProductAttribute, ProductAttributeOption
)

class CategoryType(DjangoObjectType):
    class Meta:
        model = Category
        fields = "__all__"

class ProductImageType(DjangoObjectType):
    image_url = graphene.String()

    class Meta:
        model = ProductImage
        fields = "__all__"

    def resolve_image_url(self, info):
        if self.image:
            request = info.context
            if hasattr(request, 'build_absolute_uri'):
                return request.build_absolute_uri(self.image.url)
            return f"http://localhost:8000{self.image.url}"
        return None

class ProductAttributeType(DjangoObjectType):
    class Meta:
        model = ProductAttribute
        fields = "__all__"

class ProductAttributeOptionType(DjangoObjectType):
    image_url = graphene.String()

    class Meta:
        model = ProductAttributeOption
        fields = "__all__"

    def resolve_image_url(self, info):
        if self.image:
            request = info.context
            if hasattr(request, 'build_absolute_uri'):
                return request.build_absolute_uri(self.image.url)
            return f"http://localhost:8000{self.image.url}"
        return None

class ProductVariantType(DjangoObjectType):
    color_name = graphene.String()
    size_name = graphene.String()
    is_in_stock = graphene.Boolean()

    class Meta:
        model = ProductVariant
        fields = "__all__"

    def resolve_color_name(self, info):
        return self.color_name

    def resolve_size_name(self, info):
        return self.size_name

    def resolve_is_in_stock(self, info):
        return self.is_in_stock

class ProductType(DjangoObjectType):
    min_price = graphene.Float()
    max_price = graphene.Float()
    total_stock = graphene.Int()
    available_colors = graphene.List(ProductAttributeOptionType)
    gallery_images = graphene.List(ProductImageType)

    class Meta:
        model = Product
        fields = "__all__"

    def resolve_min_price(self, info):
        return float(self.min_price)

    def resolve_max_price(self, info):
        return float(self.max_price)

    def resolve_total_stock(self, info):
        return self.total_stock

    def resolve_available_colors(self, info):
        return self.available_colors.all() if hasattr(self, 'available_colors') else []

    def resolve_gallery_images(self, info):
        return self.gallery_images.all()
