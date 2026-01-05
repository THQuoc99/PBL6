import json
import graphene
from graphene import InputObjectType, Mutation
from graphene_file_upload.scalars import Upload
from django.db import transaction
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from products.models import Product, Category, ProductVariant, ProductAttribute, ProductAttributeOption, ProductImage
from store.models import Store, StoreUser
from ..types.product import ProductType, ProductVariantType, CategoryType
from ..types.productInput import (
    ProductImageInput,
    AttributeOptionInput,
    VariantInput,
    CreateProductFullInput,
)

User = get_user_model()


# ===== INPUT TYPES =====

class ProductCreateInput(InputObjectType):
    """Input cho tạo sản phẩm mới"""
    name = graphene.String(required=True, description="Tên sản phẩm")
    description = graphene.String(required=True, description="Mô tả sản phẩm")
    category_id = graphene.Int(required=True, description="ID danh mục")
    base_price = graphene.Decimal(required=True, description="Giá cơ bản")
    brand = graphene.String(description="Thương hiệu")
    model_code = graphene.String(description="Mã model")
    is_active = graphene.Boolean(default_value=True, description="Trạng thái hoạt động")


class ProductUpdateInput(InputObjectType):
    """Input cho cập nhật sản phẩm"""
    name = graphene.String(description="Tên sản phẩm")
    description = graphene.String(description="Mô tả sản phẩm")
    category_id = graphene.Int(description="ID danh mục")
    base_price = graphene.Decimal(description="Giá cơ bản")
    brand = graphene.String(description="Thương hiệu")
    model_code = graphene.String(description="Mã model")
    is_active = graphene.Boolean(description="Trạng thái hoạt động")


class ProductVariantCreateInput(InputObjectType):
    """Input cho tạo biến thể sản phẩm"""
    product_id = graphene.Int(required=True, description="ID sản phẩm")
    sku = graphene.String(required=True, description="Mã SKU")
    price = graphene.Decimal(required=True, description="Giá")
    stock = graphene.Int(required=True, description="Tồn kho")
    weight = graphene.Decimal(description="Khối lượng")
    image_url = graphene.String(description="URL hình ảnh")
    option_combinations = graphene.JSONString(description="Kết hợp tùy chọn")
    is_active = graphene.Boolean(default_value=True, description="Trạng thái")


class ProductVariantUpdateInput(InputObjectType):
    """Input cho cập nhật biến thể"""
    sku = graphene.String(description="Mã SKU")
    price = graphene.Decimal(description="Giá")
    stock = graphene.Int(description="Tồn kho")
    weight = graphene.Decimal(description="Khối lượng")
    image_url = graphene.String(description="URL hình ảnh")
    option_combinations = graphene.JSONString(description="Kết hợp tùy chọn")
    is_active = graphene.Boolean(description="Trạng thái")


class CategoryCreateInput(InputObjectType):
    """Input cho tạo danh mục"""
    name = graphene.String(required=True, description="Tên danh mục")
    description = graphene.String(description="Mô tả danh mục")
    parent_id = graphene.Int(description="ID danh mục cha")
    thumbnail_image_url = graphene.String(description="URL ảnh đại diện danh mục")
    is_active = graphene.Boolean(default_value=True, description="Trạng thái")


class CategoryUpdateInput(InputObjectType):
    """Input cho cập nhật danh mục"""
    name = graphene.String(description="Tên danh mục")
    description = graphene.String(description="Mô tả danh mục")
    parent_id = graphene.Int(description="ID danh mục cha")
    thumbnail_image_url = graphene.String(description="URL ảnh đại diện danh mục")
    is_active = graphene.Boolean(description="Trạng thái")


# ===== PRODUCT MUTATIONS =====




class ProductDelete(Mutation):
    """Mutation xóa sản phẩm (soft delete)"""
    
    class Arguments:
        id = graphene.Int(required=True)
    
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)
    
    def mutate(self, info, id):
        user = info.context.user
        
        if not user.is_authenticated:
            return ProductDelete(
                success=False,
                errors=["Authentication required"]
            )
        
        try:
            product = Product.objects.get(product_id=id)
        except Product.DoesNotExist:
            return ProductDelete(
                success=False,
                errors=["Product not found"]
            )
        
        # Kiểm tra quyền
        # Kiểm tra quyền: sử dụng Store membership (StoreUser) hoặc staff
        try:
            has_perm = False
            if user.is_staff:
                has_perm = True
            else:
                # user phải là thành viên của store (owner/admin/manager)
                if StoreUser.objects.filter(store=product.store, user=user).exists():
                    has_perm = True

            if not has_perm:
                return ProductDelete(
                    success=False,
                    errors=["Permission denied"]
                )
        except Exception:
            return ProductDelete(
                success=False,
                errors=["Permission check failed"]
            )
        
        try:
            # Soft delete - chỉ set is_active = False
            product.is_active = False
            product.save()
            
            # Cũng deactivate tất cả variants
            product.variants.update(is_active=False)
            
            return ProductDelete(
                success=True,
                errors=[]
            )
            
        except Exception as e:
            return ProductDelete(
                success=False,
                errors=[f"Error deleting product: {str(e)}"]
            )


# ===== PRODUCT VARIANT MUTATIONS =====

class CreateProductFull(Mutation):
    """Tạo sản phẩm đầy đủ (hỗ trợ Upload cho ảnh và attribute image)"""

    class Arguments:
        input = CreateProductFullInput(required=True)

    success = graphene.Boolean()
    product = graphene.Field(lambda: ProductType)
    errors = graphene.List(graphene.String)

    @classmethod
    def mutate(cls, root, info, input):
        user = info.context.user
        if not user or not user.is_authenticated:
            return CreateProductFull(success=False, errors=["Authentication required"])

        # Validate store
        try:
            store = Store.objects.get(store_id=input.storeId)
        except Store.DoesNotExist:
            return CreateProductFull(success=False, errors=["Store not found"])

        # Check permission: store membership or staff
        has_perm = False
        if user.is_staff:
            has_perm = True
        else:
            if StoreUser.objects.filter(store=store, user=user, role__in=['owner','admin','manager']).exists():
                has_perm = True

        if not has_perm:
            return CreateProductFull(success=False, errors=["Permission denied for store"])

        # Validate category
        try:
            category = Category.objects.get(category_id=input.categoryId)
        except Category.DoesNotExist:
            return CreateProductFull(success=False, errors=["Category not found"])

        # DEBUG: dump request.FILES to help diagnose multipart upload issues
        try:
            request = info.context
            # request may be a HttpRequest or similar
            files_keys = list(getattr(request, 'FILES', {}).keys())
            print("DEBUG CreateProductFull: request.FILES keys:", files_keys)
            for k, f in getattr(request, 'FILES', {}).items():
                try:
                    name = getattr(f, 'name', None)
                    size = getattr(f, 'size', None) or getattr(f, '_size', None)
                    ctype = getattr(f, 'content_type', None)
                    print(f"DEBUG CreateProductFull FILE {k}: name={name} size={size} content_type={ctype}")
                except Exception as _e:
                    print("DEBUG CreateProductFull: error reading file object", _e)
        except Exception as _e:
            print("DEBUG CreateProductFull: failed to inspect request.FILES", _e)

        # Begin transaction to create product and related objects
        try:
            with transaction.atomic():
                product = Product.objects.create(
                    store=store,
                    category=category,
                    name=input.name,
                    description=input.description,
                    base_price=input.basePrice,
                    brand_id=getattr(input, 'brandId', None),
                    is_featured=getattr(input, 'isFeatured', False),
                    is_active=getattr(input, 'isActive', True)
                )

                # slug handling
                if getattr(input, 'slug', None):
                    product.slug = input.slug
                    product.save()

                # size guide image
                if getattr(input, 'sizeGuideImage', None):
                    from products.utils import validate_image, resize_image
                    img = input.sizeGuideImage
                    v = validate_image(img)
                    if not v['valid']:
                        raise ValueError(f"sizeGuideImage: {v['error']}")
                    resized = resize_image(img)
                    # ensure the returned ContentFile has a name (Django requires File.name)
                    try:
                        orig_name = getattr(img, 'name', None) or 'sizeguide.jpg'
                        base = orig_name.rsplit('.', 1)[0]
                        resized.name = f"{base}.jpg"
                    except Exception:
                        try:
                            resized.name = 'sizeguide.jpg'
                        except Exception:
                            pass
                    product.size_guide_image = resized
                    product.save()

                # images (gallery)
                if getattr(input, 'images', None):
                    from products.utils import validate_image, resize_image
                    for img_in in input.images:
                        v = validate_image(img_in.image)
                        if not v['valid']:
                            raise ValueError(f"Image validation failed: {v['error']}")
                        resized = resize_image(img_in.image)
                        # ensure ContentFile has a name
                        try:
                            orig_name = getattr(img_in.image, 'name', None) or 'image.jpg'
                            base = orig_name.rsplit('.', 1)[0]
                            resized.name = f"{base}.jpg"
                        except Exception:
                            try:
                                resized.name = 'image.jpg'
                            except Exception:
                                pass
                        # if thumbnail, unset existing thumbnails
                        if getattr(img_in, 'isThumbnail', False):
                            ProductImage.objects.filter(product=product, is_thumbnail=True).update(is_thumbnail=False)
                        ProductImage.objects.create(
                            product=product,
                            image=resized,
                            is_thumbnail=getattr(img_in, 'isThumbnail', False),
                            alt_text=getattr(img_in, 'altText', None),
                            display_order=getattr(img_in, 'displayOrder', 0)
                        )

                # attribute options
                if getattr(input, 'attributeOptions', None):
                    from products.utils import validate_image, resize_image
                    for opt in input.attributeOptions:
                        # attributeId may be numeric (attribute_id) or a code/name like 'color'
                        raw_attr_id = getattr(opt, 'attributeId')
                        attribute = None
                        # try numeric id first
                        try:
                            if raw_attr_id is not None and (isinstance(raw_attr_id, int) or (isinstance(raw_attr_id, str) and str(raw_attr_id).isdigit())):
                                attribute = ProductAttribute.objects.get(attribute_id=int(raw_attr_id))
                        except ProductAttribute.DoesNotExist:
                            attribute = None

                        # fallback: try lookup by code or name (case-insensitive)
                        if attribute is None and raw_attr_id is not None:
                            try:
                                attribute = ProductAttribute.objects.filter(code__iexact=str(raw_attr_id)).first()
                            except Exception:
                                attribute = None
                        if attribute is None and raw_attr_id is not None:
                            try:
                                attribute = ProductAttribute.objects.filter(name__iexact=str(raw_attr_id)).first()
                            except Exception:
                                attribute = None

                        if attribute is None:
                            raise ValueError(f"Attribute id {raw_attr_id} not found")

                        option_kwargs = {
                            'product': product,
                            # assign by attribute_id to avoid passing a raw string
                            'attribute_id': getattr(attribute, 'attribute_id', None),
                            'value': getattr(opt, 'value'),
                            'value_code': getattr(opt, 'valueCode', None),
                            'display_order': getattr(opt, 'displayOrder', 0)
                        }

                        # handle image for option
                        if getattr(opt, 'image', None):
                            v = validate_image(opt.image)
                            if not v['valid']:
                                raise ValueError(f"Attribute option image: {v['error']}")
                            resized = resize_image(opt.image, max_width=300, max_height=200)
                            # ensure ContentFile has a name
                            try:
                                orig_name = getattr(opt.image, 'name', None) or 'option.jpg'
                                base = orig_name.rsplit('.', 1)[0]
                                resized.name = f"{base}.jpg"
                            except Exception:
                                try:
                                    resized.name = 'option.jpg'
                                except Exception:
                                    pass
                            option_kwargs['image'] = resized

                        ProductAttributeOption.objects.create(**option_kwargs)

                # variants
                if getattr(input, 'variants', None):
                    for v_in in input.variants:
                        sku = getattr(v_in, 'sku', None) or None
                        # generate SKU if not provided
                        if not sku:
                            base = product.slug or product.model_code or str(product.product_id)
                            candidate = f"{base}-1"
                            idx = 1
                            while ProductVariant.objects.filter(sku=candidate).exists():
                                idx += 1
                                candidate = f"{base}-{idx}"
                            sku = candidate

                        option_combinations = getattr(v_in, 'optionCombinations')
                        # ensure JSON string stored as JSON/dict
                        if isinstance(option_combinations, str):
                            try:
                                option_combinations = json.loads(option_combinations)
                            except Exception:
                                raise ValueError("Invalid JSON for optionCombinations")

                        ProductVariant.objects.create(
                            product=product,
                            sku=sku,
                            price=v_in.price,
                            stock=v_in.stock,
                            option_combinations=option_combinations
                        )

                return CreateProductFull(success=True, product=product, errors=[])

        except Exception as e:
            # Build diagnostic info from request.FILES to help frontend debugging
            try:
                request = info.context
                files_info = {}
                for k, f in getattr(request, 'FILES', {}).items():
                    try:
                        files_info[k] = {
                            'name': getattr(f, 'name', None),
                            'size': getattr(f, 'size', None) or getattr(f, '_size', None),
                            'content_type': getattr(f, 'content_type', None)
                        }
                    except Exception as _fi:
                        files_info[k] = {'error': str(_fi)}
            except Exception as _e:
                files_info = {'error_inspecting_files': str(_e)}

            err_msg = str(e)
            diag = {'request_files': files_info}
            # Return original error plus a machine-readable debug payload
            return CreateProductFull(success=False, product=None, errors=[err_msg, f"DEBUG_FILES:{json.dumps(diag)}"])


class UpdateProductFull(Mutation):
    """Cập nhật sản phẩm đầy đủ (tương tự CreateProductFull nhưng nhận productId)"""

    class Arguments:
        productId = graphene.Int(required=True)
        input = CreateProductFullInput(required=True)

    success = graphene.Boolean()
    product = graphene.Field(lambda: ProductType)
    errors = graphene.List(graphene.String)

    @classmethod
    def mutate(cls, root, info, productId, input):
        user = info.context.user
        if not user or not user.is_authenticated:
            return UpdateProductFull(success=False, errors=["Authentication required"])

        # locate product
        try:
            product = Product.objects.get(product_id=productId)
        except Product.DoesNotExist:
            return UpdateProductFull(success=False, errors=["Product not found"])

        # permission: owner of store or staff
        has_perm = False
        if user.is_staff:
            has_perm = True
        else:
            if StoreUser.objects.filter(store=product.store, user=user, role__in=['owner','admin','manager']).exists():
                has_perm = True

        if not has_perm:
            return UpdateProductFull(success=False, errors=["Permission denied for store"])

        # DEBUG: inspect incoming files
        try:
            request = info.context
            files_keys = list(getattr(request, 'FILES', {}).keys())
            print("DEBUG UpdateProductFull: request.FILES keys:", files_keys)
            for k, f in getattr(request, 'FILES', {}).items():
                try:
                    name = getattr(f, 'name', None)
                    size = getattr(f, 'size', None) or getattr(f, '_size', None)
                    ctype = getattr(f, 'content_type', None)
                    print(f"DEBUG UpdateProductFull FILE {k}: name={name} size={size} content_type={ctype}")
                except Exception as _e:
                    print("DEBUG UpdateProductFull: error reading file object", _e)
        except Exception as _e:
            print("DEBUG UpdateProductFull: failed to inspect request.FILES", _e)

        try:
            with transaction.atomic():
                # update basic fields if provided
                if getattr(input, 'name', None) is not None:
                    product.name = input.name
                if getattr(input, 'description', None) is not None:
                    product.description = input.description
                if getattr(input, 'basePrice', None) is not None:
                    product.base_price = input.basePrice
                if getattr(input, 'brandId', None) is not None:
                    product.brand_id = input.brandId
                if getattr(input, 'isFeatured', None) is not None:
                    product.is_featured = input.isFeatured
                if getattr(input, 'isActive', None) is not None:
                    product.is_active = input.isActive

                # category update
                if getattr(input, 'categoryId', None) is not None:
                    try:
                        category = Category.objects.get(category_id=input.categoryId)
                        product.category = category
                    except Category.DoesNotExist:
                        raise ValueError("Category not found")

                # slug
                if getattr(input, 'slug', None):
                    product.slug = input.slug

                product.save()

                # size guide image
                if getattr(input, 'sizeGuideImage', None):
                    from products.utils import validate_image, resize_image
                    img = input.sizeGuideImage
                    v = validate_image(img)
                    if not v['valid']:
                        raise ValueError(f"sizeGuideImage: {v['error']}")
                    resized = resize_image(img)
                    try:
                        orig_name = getattr(img, 'name', None) or 'sizeguide.jpg'
                        base = orig_name.rsplit('.', 1)[0]
                        resized.name = f"{base}.jpg"
                    except Exception:
                        try:
                            resized.name = 'sizeguide.jpg'
                        except Exception:
                            pass
                    product.size_guide_image = resized
                    product.save()

                # images (gallery) - append new images
                if getattr(input, 'images', None):
                    from products.utils import validate_image, resize_image
                    for img_in in input.images:
                        v = validate_image(img_in.image)
                        if not v['valid']:
                            raise ValueError(f"Image validation failed: {v['error']}")
                        resized = resize_image(img_in.image)
                        try:
                            orig_name = getattr(img_in.image, 'name', None) or 'image.jpg'
                            base = orig_name.rsplit('.', 1)[0]
                            resized.name = f"{base}.jpg"
                        except Exception:
                            try:
                                resized.name = 'image.jpg'
                            except Exception:
                                pass
                        if getattr(img_in, 'isThumbnail', False):
                            ProductImage.objects.filter(product=product, is_thumbnail=True).update(is_thumbnail=False)
                        ProductImage.objects.create(
                            product=product,
                            image=resized,
                            is_thumbnail=getattr(img_in, 'isThumbnail', False),
                            alt_text=getattr(img_in, 'altText', None),
                            display_order=getattr(img_in, 'displayOrder', 0)
                        )

                # attribute options - append new options
                if getattr(input, 'attributeOptions', None):
                    from products.utils import validate_image, resize_image
                    for opt in input.attributeOptions:
                        raw_attr_id = getattr(opt, 'attributeId')
                        attribute = None
                        try:
                            if raw_attr_id is not None and (isinstance(raw_attr_id, int) or (isinstance(raw_attr_id, str) and str(raw_attr_id).isdigit())):
                                attribute = ProductAttribute.objects.get(attribute_id=int(raw_attr_id))
                        except ProductAttribute.DoesNotExist:
                            attribute = None

                        if attribute is None and raw_attr_id is not None:
                            try:
                                attribute = ProductAttribute.objects.filter(code__iexact=str(raw_attr_id)).first()
                            except Exception:
                                attribute = None
                        if attribute is None and raw_attr_id is not None:
                            try:
                                attribute = ProductAttribute.objects.filter(name__iexact=str(raw_attr_id)).first()
                            except Exception:
                                attribute = None

                        if attribute is None:
                            raise ValueError(f"Attribute id {raw_attr_id} not found")

                        option_kwargs = {
                            'product': product,
                            'attribute_id': getattr(attribute, 'attribute_id', None),
                            'value': getattr(opt, 'value'),
                            'value_code': getattr(opt, 'valueCode', None),
                            'display_order': getattr(opt, 'displayOrder', 0)
                        }

                        if getattr(opt, 'image', None):
                            v = validate_image(opt.image)
                            if not v['valid']:
                                raise ValueError(f"Attribute option image: {v['error']}")
                            resized = resize_image(opt.image, max_width=300, max_height=200)
                            try:
                                orig_name = getattr(opt.image, 'name', None) or 'option.jpg'
                                base = orig_name.rsplit('.', 1)[0]
                                resized.name = f"{base}.jpg"
                            except Exception:
                                try:
                                    resized.name = 'option.jpg'
                                except Exception:
                                    pass
                            option_kwargs['image'] = resized

                        # Avoid creating duplicate attribute option values for same product+attribute+value
                        try:
                            existing = ProductAttributeOption.objects.filter(
                                product=product,
                                attribute_id=option_kwargs.get('attribute_id'),
                                value=option_kwargs.get('value')
                            ).first()
                            if existing:
                                # If frontend provided a new image file, update the existing option's image
                                if 'image' in option_kwargs and option_kwargs['image'] is not None:
                                    existing.image = option_kwargs['image']
                                    existing.display_order = option_kwargs.get('display_order', existing.display_order)
                                    if option_kwargs.get('value_code') is not None:
                                        existing.value_code = option_kwargs.get('value_code')
                                    existing.save()
                                # else: value already exists, skip creating duplicate
                            else:
                                ProductAttributeOption.objects.create(**option_kwargs)
                        except Exception as _opt_e:
                            # If anything unexpected happens, raise to be handled by outer transaction
                            raise

                # variants - append new variants if provided
                if getattr(input, 'variants', None):
                    for v_in in input.variants:
                        # Prefer explicit variant id for updates
                        vid = getattr(v_in, 'variantId', None) or getattr(v_in, 'id', None) or None
                        sku = getattr(v_in, 'sku', None)
                        price = getattr(v_in, 'price', None)
                        stock = getattr(v_in, 'stock', None)

                        option_combinations = getattr(v_in, 'optionCombinations')
                        if isinstance(option_combinations, str):
                            try:
                                option_combinations = json.loads(option_combinations)
                            except Exception:
                                raise ValueError("Invalid JSON for optionCombinations")

                        # If variant id provided, update that variant
                        if vid is not None:
                            try:
                                variant = ProductVariant.objects.get(variant_id=int(vid))
                                if sku:
                                    variant.sku = sku
                                if price is not None:
                                    variant.price = price
                                if stock is not None:
                                    variant.stock = stock
                                if option_combinations is not None:
                                    variant.option_combinations = option_combinations
                                variant.save()
                                continue
                            except ProductVariant.DoesNotExist:
                                # fallthrough to creation logic
                                variant = None

                        # Try to find existing variant by SKU for this product
                        existing_variant = None
                        if sku:
                            existing_variant = ProductVariant.objects.filter(product=product, sku=sku).first()

                        if existing_variant:
                            # update fields on found variant
                            if price is not None:
                                existing_variant.price = price
                            if stock is not None:
                                existing_variant.stock = stock
                            if option_combinations is not None:
                                existing_variant.option_combinations = option_combinations
                            existing_variant.save()
                            continue

                        # Otherwise create new variant (ensure unique SKU)
                        if not sku:
                            base = product.slug or product.model_code or str(product.product_id)
                            candidate = f"{base}-1"
                            idx = 1
                            while ProductVariant.objects.filter(sku=candidate).exists():
                                idx += 1
                                candidate = f"{base}-{idx}"
                            sku = candidate

                        ProductVariant.objects.create(
                            product=product,
                            sku=sku,
                            price=price,
                            stock=stock,
                            option_combinations=option_combinations
                        )

                return UpdateProductFull(success=True, product=product, errors=[])

        except Exception as e:
            try:
                request = info.context
                files_info = {}
                for k, f in getattr(request, 'FILES', {}).items():
                    try:
                        files_info[k] = {
                            'name': getattr(f, 'name', None),
                            'size': getattr(f, 'size', None) or getattr(f, '_size', None),
                            'content_type': getattr(f, 'content_type', None)
                        }
                    except Exception as _fi:
                        files_info[k] = {'error': str(_fi)}
            except Exception as _e:
                files_info = {'error_inspecting_files': str(_e)}

            err_msg = str(e)
            diag = {'request_files': files_info}
            return UpdateProductFull(success=False, product=None, errors=[err_msg, f"DEBUG_FILES:{json.dumps(diag)}"])





# ===== CATEGORY MUTATIONS =====

class CategoryCreate(Mutation):
    """Mutation tạo danh mục (chỉ admin)"""
    
    class Arguments:
        input = CategoryCreateInput(required=True)
    
    success = graphene.Boolean()
    category = graphene.Field(CategoryType)
    errors = graphene.List(graphene.String)
    
    def mutate(self, info, input):
        user = info.context.user
        
        # Chỉ admin có thể tạo category
        if not user.is_authenticated or not user.is_staff:
            return CategoryCreate(
                success=False,
                errors=["Admin permission required"]
            )
        
        try:
            # Kiểm tra parent category nếu có
            parent = None
            if input.get('parent_id'):
                try:
                    parent = Category.objects.get(
                        category_id=input.parent_id,
                        is_active=True
                    )
                except Category.DoesNotExist:
                    return CategoryCreate(
                        success=False,
                        errors=["Parent category not found"]
                    )
            
            # Tạo category
            category_data = {
                'name': input.name,
                'description': input.get('description'),
                'parent': parent,
                'is_active': input.get('is_active', True)
            }
            
            # Xử lý thumbnail image nếu có
            if input.get('thumbnail_image_url'):
                # TODO: Implement image upload logic
                # Có thể sử dụng Django's ImageField hoặc xử lý URL
                category_data['thumbnail_image'] = input.thumbnail_image_url
            
            category = Category.objects.create(**category_data)
            
            return CategoryCreate(
                success=True,
                category=category,
                errors=[]
            )
            
        except ValidationError as e:
            return CategoryCreate(
                success=False,
                errors=[str(e)]
            )
        except Exception as e:
            return CategoryCreate(
                success=False,
                errors=[f"Error creating category: {str(e)}"]
            )


# ===== INVENTORY MUTATIONS =====

class ProductVariantStockUpdate(Mutation):
    """Mutation cập nhật tồn kho"""
    
    class Arguments:
        variant_id = graphene.Int(required=True)
        stock_change = graphene.Int(required=True, description="Thay đổi stock (+/-)")
        reason = graphene.String(description="Lý do thay đổi")
    
    success = graphene.Boolean()
    variant = graphene.Field(ProductVariantType)
    new_stock = graphene.Int()
    errors = graphene.List(graphene.String)
    
    def mutate(self, info, variant_id, stock_change, reason=None):
        user = info.context.user
        
        if not user.is_authenticated:
            return ProductVariantStockUpdate(
                success=False,
                errors=["Authentication required"]
            )
        
        try:
            variant = ProductVariant.objects.get(variant_id=variant_id)
        except ProductVariant.DoesNotExist:
            return ProductVariantStockUpdate(
                success=False,
                errors=["Variant not found"]
            )
        
        # Kiểm tra quyền
        if variant.product.seller != user and not user.is_staff:
            return ProductVariantStockUpdate(
                success=False,
                errors=["Permission denied"]
            )
        
        try:
            # Tính stock mới
            new_stock = variant.stock + stock_change
            
            # Kiểm tra stock không âm
            if new_stock < 0:
                return ProductVariantStockUpdate(
                    success=False,
                    errors=["Stock cannot be negative"]
                )
            
            variant.stock = new_stock
            variant.save()
            
            # TODO: Log stock history với reason
            
            return ProductVariantStockUpdate(
                success=True,
                variant=variant,
                new_stock=new_stock,
                errors=[]
            )
            
        except Exception as e:
            return ProductVariantStockUpdate(
                success=False,
                errors=[f"Error updating stock: {str(e)}"]
            )


# ===== MISSING MUTATIONS =====

class CategoryUpdateInput(InputObjectType):
    """Input cho cập nhật danh mục"""
    name = graphene.String(description="Tên danh mục")
    description = graphene.String(description="Mô tả danh mục")
    parent_id = graphene.Int(description="ID danh mục cha")
    is_active = graphene.Boolean(description="Trạng thái hoạt động")


class CategoryUpdate(Mutation):
    """Cập nhật danh mục"""
    
    class Arguments:
        id = graphene.Int(required=True, description="ID danh mục")
        input = CategoryUpdateInput(required=True)
    
    success = graphene.Boolean()
    category = graphene.Field(CategoryType)
    errors = graphene.List(graphene.String)
    
    def mutate(self, info, id, input):
        try:
            category = Category.objects.get(category_id=id)
            
            # Cập nhật các trường
            if input.name is not None:
                category.name = input.name
            if input.description is not None:
                category.description = input.description
            if input.parent_id is not None:
                category.parent_id = input.parent_id
            if input.is_active is not None:
                category.is_active = input.is_active
            
            category.save()
            
            return CategoryUpdate(
                success=True,
                category=category,
                errors=[]
            )
            
        except Category.DoesNotExist:
            return CategoryUpdate(
                success=False,
                errors=["Category not found"]
            )
        except Exception as e:
            return CategoryUpdate(
                success=False,
                errors=[f"Error updating category: {str(e)}"]
            )


class CategoryDelete(Mutation):
    """Xóa danh mục"""
    
    class Arguments:
        id = graphene.Int(required=True, description="ID danh mục")
    
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)
    
    def mutate(self, info, id):
        try:
            category = Category.objects.get(category_id=id)
            
            # Kiểm tra có sản phẩm không
            if category.products.exists():
                return CategoryDelete(
                    success=False,
                    errors=["Cannot delete category with products"]
                )
            
            category.delete()
            
            return CategoryDelete(
                success=True,
                errors=[]
            )
            
        except Category.DoesNotExist:
            return CategoryDelete(
                success=False,
                errors=["Category not found"]
            )
        except Exception as e:
            return CategoryDelete(
                success=False,
                errors=[f"Error deleting category: {str(e)}"]
            )


class StockUpdate(Mutation):
    """Cập nhật tồn kho (alias cho ProductVariantStockUpdate)"""
    
    class Arguments:
        variant_id = graphene.Int(required=True)
        new_stock = graphene.Int(required=True)
        reason = graphene.String()
    
    success = graphene.Boolean()
    variant = graphene.Field(ProductVariantType)
    new_stock = graphene.Int()
    errors = graphene.List(graphene.String)
    
    def mutate(self, info, variant_id, new_stock, reason=None):
        # Sử dụng lại logic từ ProductVariantStockUpdate
        stock_update = ProductVariantStockUpdate()
        return stock_update.mutate(info, variant_id, new_stock, reason)


class PriceUpdate(Mutation):
    """Cập nhật giá sản phẩm"""
    
    class Arguments:
        variant_id = graphene.Int(required=True)
        new_price = graphene.Decimal(required=True)
        reason = graphene.String()
    
    success = graphene.Boolean()
    variant = graphene.Field(ProductVariantType)
    old_price = graphene.Decimal()
    new_price = graphene.Decimal()
    errors = graphene.List(graphene.String)
    
    def mutate(self, info, variant_id, new_price, reason=None):
        try:
            variant = ProductVariant.objects.get(variant_id=variant_id)
            old_price = variant.price
            
            variant.price = new_price
            variant.save()
            
            # TODO: Log price history với reason
            
            return PriceUpdate(
                success=True,
                variant=variant,
                old_price=old_price,
                new_price=new_price,
                errors=[]
            )
            
        except ProductVariant.DoesNotExist:
            return PriceUpdate(
                success=False,
                errors=["Product variant not found"]
            )
        except Exception as e:
            return PriceUpdate(
                success=False,
                errors=[f"Error updating price: {str(e)}"]
            )


# ===== CATEGORY MUTATIONS =====

class CategoryCreate(Mutation):
    """Mutation tạo danh mục mới"""
    
    class Arguments:
        input = CategoryCreateInput(required=True)
    
    success = graphene.Boolean()
    category = graphene.Field(CategoryType)
    errors = graphene.List(graphene.String)
    
    def mutate(self, info, input):
        try:
            # Kiểm tra parent category nếu có
            parent_category = None
            if input.parent_id:
                try:
                    parent_category = Category.objects.get(
                        category_id=input.parent_id,
                        is_active=True
                    )
                except Category.DoesNotExist:
                    return CategoryCreate(
                        success=False,
                        errors=["Parent category not found or inactive"]
                    )
            
            # Tạo category mới
            category = Category.objects.create(
                name=input.name,
                description=input.description or "",
                parent=parent_category,
                is_active=input.is_active
            )
            
            return CategoryCreate(
                success=True,
                category=category,
                errors=[]
            )
            
        except Exception as e:
            return CategoryCreate(
                success=False,
                errors=[f"Error creating category: {str(e)}"]
            )


class CategoryUpdate(Mutation):
    """Mutation cập nhật danh mục"""
    
    class Arguments:
        id = graphene.ID(required=True)
        input = CategoryCreateInput(required=True)  # Reuse input type
    
    success = graphene.Boolean()
    category = graphene.Field(CategoryType)
    errors = graphene.List(graphene.String)
    
    def mutate(self, info, id, input):
        try:
            # Lấy category cần update
            category = Category.objects.get(category_id=id)
            
            # Kiểm tra parent category nếu có
            if input.parent_id:
                try:
                    parent_category = Category.objects.get(
                        category_id=input.parent_id,
                        is_active=True
                    )
                    category.parent = parent_category
                except Category.DoesNotExist:
                    return CategoryUpdate(
                        success=False,
                        errors=["Parent category not found or inactive"]
                    )
            
            # Update fields
            if input.name:
                category.name = input.name
            if input.description is not None:
                category.description = input.description
            if input.is_active is not None:
                category.is_active = input.is_active
            
            category.save()
            
            return CategoryUpdate(
                success=True,
                category=category,
                errors=[]
            )
            
        except Category.DoesNotExist:
            return CategoryUpdate(
                success=False,
                errors=["Category not found"]
            )
        except Exception as e:
            return CategoryUpdate(
                success=False,
                errors=[f"Error updating category: {str(e)}"]
            )


class CategoryDelete(Mutation):
    """Mutation xóa danh mục"""
    
    class Arguments:
        id = graphene.ID(required=True)
    
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)
    
    def mutate(self, info, id):
        try:
            category = Category.objects.get(category_id=id)
            
            # Kiểm tra có subcategories không
            if category.subcategories.exists():
                return CategoryDelete(
                    success=False,
                    errors=["Cannot delete category with subcategories"]
                )
            
            # Kiểm tra có sản phẩm không
            if category.products.exists():
                return CategoryDelete(
                    success=False,
                    errors=["Cannot delete category with products"]
                )
            
            category.delete()
            
            return CategoryDelete(
                success=True,
                errors=[]
            )
            
        except Category.DoesNotExist:
            return CategoryDelete(
                success=False,
                errors=["Category not found"]
            )
        except Exception as e:
            return CategoryDelete(
                success=False,
                errors=[f"Error deleting category: {str(e)}"]
            )