import graphene
from graphene_file_upload.scalars import Upload
from graphene_django.types import ErrorType
from django.db import transaction
from django.core.exceptions import ValidationError

from products.models import Product, ProductImage, ProductAttributeOption
from products.utils import validate_image, resize_image
from ..types.product import ProductImageType, ProductAttributeOptionType


class UploadProductImage(graphene.Mutation):
    """Mutation để upload ảnh sản phẩm"""
    
    class Arguments:
        product_id = graphene.ID(required=True)
        image = Upload(required=True)
        is_thumbnail = graphene.Boolean(default_value=False)
        alt_text = graphene.String()
        display_order = graphene.Int(default_value=0)
    
    product_image = graphene.Field(ProductImageType)
    errors = graphene.List(ErrorType)
    
    @classmethod
    def mutate(cls, root, info, product_id, image, **kwargs):
        try:
            with transaction.atomic():
                # Validate product tồn tại
                try:
                    product = Product.objects.get(product_id=product_id)
                except Product.DoesNotExist:
                    return UploadProductImage(
                        errors=[ErrorType(message="Sản phẩm không tồn tại")]
                    )
                
                # Validate ảnh
                validation = validate_image(image)
                if not validation['valid']:
                    return UploadProductImage(
                        errors=[ErrorType(message=validation['error'])]
                    )
                
                # Resize ảnh
                resized_image = resize_image(image)
                
                # Xử lý thumbnail unique
                is_thumbnail = kwargs.get('is_thumbnail', False)
                if is_thumbnail:
                    # Bỏ thumbnail cũ
                    ProductImage.objects.filter(
                        product=product, 
                        is_thumbnail=True
                    ).update(is_thumbnail=False)
                
                # Tạo ProductImage
                product_image = ProductImage.objects.create(
                    product=product,
                    image=resized_image,
                    is_thumbnail=is_thumbnail,
                    alt_text=kwargs.get('alt_text', f"{product.name} - Ảnh"),
                    display_order=kwargs.get('display_order', 0)
                )
                
                return UploadProductImage(product_image=product_image)
                
        except Exception as e:
            return UploadProductImage(
                errors=[ErrorType(message=f"Lỗi upload: {str(e)}")]
            )


class UploadAttributeOptionImage(graphene.Mutation):
    """Mutation để upload ảnh cho attribute option"""
    
    class Arguments:
        option_id = graphene.ID(required=True)
        image = Upload(required=True)
    
    attribute_option = graphene.Field(ProductAttributeOptionType)
    errors = graphene.List(ErrorType)
    
    @classmethod
    def mutate(cls, root, info, option_id, image):
        try:
            with transaction.atomic():
                # Validate option tồn tại
                try:
                    option = ProductAttributeOption.objects.get(option_id=option_id)
                except ProductAttributeOption.DoesNotExist:
                    return UploadAttributeOptionImage(
                        errors=[ErrorType(message="Tùy chọn không tồn tại")]
                    )
                
                # Validate ảnh
                validation = validate_image(image)
                if not validation['valid']:
                    return UploadAttributeOptionImage(
                        errors=[ErrorType(message=validation['error'])]
                    )
                
                # Resize ảnh (nhỏ hơn cho options)
                resized_image = resize_image(image, max_width=300, max_height=200)
                
                # Cập nhật option
                option.image = resized_image
                option.save()
                
                return UploadAttributeOptionImage(attribute_option=option)
                
        except Exception as e:
            return UploadAttributeOptionImage(
                errors=[ErrorType(message=f"Lỗi upload: {str(e)}")]
            )


class DeleteProductImage(graphene.Mutation):
    """Mutation để xóa ảnh sản phẩm"""
    
    class Arguments:
        image_id = graphene.ID(required=True)
    
    success = graphene.Boolean()
    errors = graphene.List(ErrorType)
    
    @classmethod
    def mutate(cls, root, info, image_id):
        try:
            with transaction.atomic():
                try:
                    image = ProductImage.objects.get(image_id=image_id)
                    image.delete()  # Signal sẽ tự động xóa file
                    return DeleteProductImage(success=True)
                except ProductImage.DoesNotExist:
                    return DeleteProductImage(
                        errors=[ErrorType(message="Ảnh không tồn tại")]
                    )
        except Exception as e:
            return DeleteProductImage(
                errors=[ErrorType(message=f"Lỗi xóa ảnh: {str(e)}")]
            )


# Thêm vào ProductMutation
class ProductImageMutation(graphene.ObjectType):
    upload_product_image = UploadProductImage.Field()
    upload_attribute_option_image = UploadAttributeOptionImage.Field()
    delete_product_image = DeleteProductImage.Field()