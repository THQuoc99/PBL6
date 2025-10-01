import graphene
from graphene import InputObjectType, Mutation
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from products.models import Product, Category, ProductVariant, ProductAttribute, ProductAttributeOption, ProductImage
from ..types.product import ProductType, ProductVariantType, CategoryType

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
    is_active = graphene.Boolean(default_value=True, description="Trạng thái")


# ===== PRODUCT MUTATIONS =====

class ProductCreate(Mutation):
    """Mutation tạo sản phẩm mới"""
    
    class Arguments:
        input = ProductCreateInput(required=True)
    
    success = graphene.Boolean()
    product = graphene.Field(ProductType)
    errors = graphene.List(graphene.String)
    
    def mutate(self, info, input):
        user = info.context.user
        # Kiểm tra authentication
        if not user.is_authenticated:
            return ProductCreate(
                success=False,
                errors=["Authentication required"]
            )
        
        try:
            # Kiểm tra category tồn tại
            try:
                category = Category.objects.get(
                    category_id=input.category_id, 
                    is_active=True
                )
            except Category.DoesNotExist:
                return ProductCreate(
                    success=False,
                    errors=["Category not found or inactive"]
                )
            
            # Tạo product
            product = Product.objects.create(
                seller=user,
                category=category,
                name=input.name,
                description=input.description,
                base_price=input.base_price,
                brand=input.get('brand'),
                model_code=input.get('model_code'),
                is_active=input.get('is_active', True)
            )
            
            return ProductCreate(
                success=True,
                product=product,
                errors=[]
            )
            
        except ValidationError as e:
            return ProductCreate(
                success=False,
                errors=[str(e)]
            )
        except Exception as e:
            return ProductCreate(
                success=False,
                errors=[f"Error creating product: {str(e)}"]
            )


class ProductUpdate(Mutation):
    """Mutation cập nhật sản phẩm"""
    
    class Arguments:
        id = graphene.Int(required=True)
        input = ProductUpdateInput(required=True)
    
    success = graphene.Boolean()
    product = graphene.Field(ProductType)
    errors = graphene.List(graphene.String)
    
    def mutate(self, info, id, input):
        user = info.context.user
        
        # Kiểm tra authentication
        if not user.is_authenticated:
            return ProductUpdate(
                success=False,
                errors=["Authentication required"]
            )
        
        try:
            # Kiểm tra product tồn tại và quyền sở hữu
            try:
                product = Product.objects.get(product_id=id)
            except Product.DoesNotExist:
                return ProductUpdate(
                    success=False,
                    errors=["Product not found"]
                )
            
            # Kiểm tra quyền sở hữu (chỉ seller hoặc admin có thể update)
            if product.seller != user and not user.is_staff:
                return ProductUpdate(
                    success=False,
                    errors=["Permission denied"]
                )
            
            # Kiểm tra category nếu có update
            if input.get('category_id'):
                try:
                    category = Category.objects.get(
                        category_id=input.category_id,
                        is_active=True
                    )
                    product.category = category
                except Category.DoesNotExist:
                    return ProductUpdate(
                        success=False,
                        errors=["Category not found or inactive"]
                    )
            
            # Cập nhật các trường
            if input.get('name') is not None:
                product.name = input.name
            if input.get('description') is not None:
                product.description = input.description
            if input.get('base_price') is not None:
                product.base_price = input.base_price
            if input.get('brand') is not None:
                product.brand = input.brand
            if input.get('model_code') is not None:
                product.model_code = input.model_code
            if input.get('is_active') is not None:
                product.is_active = input.is_active
            
            product.save()
            
            return ProductUpdate(
                success=True,
                product=product,
                errors=[]
            )
            
        except ValidationError as e:
            return ProductUpdate(
                success=False,
                errors=[str(e)]
            )
        except Exception as e:
            return ProductUpdate(
                success=False,
                errors=[f"Error updating product: {str(e)}"]
            )


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
        if product.seller != user and not user.is_staff:
            return ProductDelete(
                success=False,
                errors=["Permission denied"]
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

class ProductVariantCreate(Mutation):
    """Mutation tạo biến thể sản phẩm"""
    
    class Arguments:
        input = ProductVariantCreateInput(required=True)
    
    success = graphene.Boolean()
    variant = graphene.Field(ProductVariantType)
    errors = graphene.List(graphene.String)
    
    def mutate(self, info, input):
        user = info.context.user
        
        if not user.is_authenticated:
            return ProductVariantCreate(
                success=False,
                errors=["Authentication required"]
            )
        
        try:
            # Kiểm tra product tồn tại và quyền sở hữu
            try:
                product = Product.objects.get(product_id=input.product_id)
            except Product.DoesNotExist:
                return ProductVariantCreate(
                    success=False,
                    errors=["Product not found"]
                )
            
            if product.seller != user and not user.is_staff:
                return ProductVariantCreate(
                    success=False,
                    errors=["Permission denied"]
                )
            
            # Kiểm tra SKU unique
            if ProductVariant.objects.filter(sku=input.sku).exists():
                return ProductVariantCreate(
                    success=False,
                    errors=["SKU already exists"]
                )
            
            # Tạo variant
            variant = ProductVariant.objects.create(
                product=product,
                sku=input.sku,
                price=input.price,
                stock=input.stock,
                weight=input.get('weight', 0.1),
                option_combinations=input.get('option_combinations', {}),
                is_active=input.get('is_active', True)
            )
            
            return ProductVariantCreate(
                success=True,
                variant=variant,
                errors=[]
            )
            
        except ValidationError as e:
            return ProductVariantCreate(
                success=False,
                errors=[str(e)]
            )
        except Exception as e:
            return ProductVariantCreate(
                success=False,
                errors=[f"Error creating variant: {str(e)}"]
            )


class ProductVariantUpdate(Mutation):
    """Mutation cập nhật biến thể"""
    
    class Arguments:
        id = graphene.Int(required=True)
        input = ProductVariantUpdateInput(required=True)
    
    success = graphene.Boolean()
    variant = graphene.Field(ProductVariantType)
    errors = graphene.List(graphene.String)
    
    def mutate(self, info, id, input):
        user = info.context.user
        
        if not user.is_authenticated:
            return ProductVariantUpdate(
                success=False,
                errors=["Authentication required"]
            )
        
        try:
            variant = ProductVariant.objects.get(variant_id=id)
        except ProductVariant.DoesNotExist:
            return ProductVariantUpdate(
                success=False,
                errors=["Variant not found"]
            )
        
        # Kiểm tra quyền
        if variant.product.seller != user and not user.is_staff:
            return ProductVariantUpdate(
                success=False,
                errors=["Permission denied"]
            )
        
        try:
            # Kiểm tra SKU unique nếu có update
            if input.get('sku') and input.sku != variant.sku:
                if ProductVariant.objects.filter(sku=input.sku).exists():
                    return ProductVariantUpdate(
                        success=False,
                        errors=["SKU already exists"]
                    )
                variant.sku = input.sku
            
            # Cập nhật fields
            if input.get('price') is not None:
                variant.price = input.price
            if input.get('stock') is not None:
                variant.stock = input.stock
            if input.get('weight') is not None:
                variant.weight = input.weight
            if input.get('image_url') is not None:
                variant.image_url = input.image_url
            if input.get('option_combinations') is not None:
                variant.option_combinations = input.option_combinations
            if input.get('is_active') is not None:
                variant.is_active = input.is_active
            
            variant.save()
            
            return ProductVariantUpdate(
                success=True,
                variant=variant,
                errors=[]
            )
            
        except ValidationError as e:
            return ProductVariantUpdate(
                success=False,
                errors=[str(e)]
            )
        except Exception as e:
            return ProductVariantUpdate(
                success=False,
                errors=[f"Error updating variant: {str(e)}"]
            )


class ProductVariantDelete(Mutation):
    """Mutation xóa biến thể"""
    
    class Arguments:
        id = graphene.Int(required=True)
    
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)
    
    def mutate(self, info, id):
        user = info.context.user
        
        if not user.is_authenticated:
            return ProductVariantDelete(
                success=False,
                errors=["Authentication required"]
            )
        
        try:
            variant = ProductVariant.objects.get(variant_id=id)
        except ProductVariant.DoesNotExist:
            return ProductVariantDelete(
                success=False,
                errors=["Variant not found"]
            )
        
        # Kiểm tra quyền
        if variant.product.seller != user and not user.is_staff:
            return ProductVariantDelete(
                success=False,
                errors=["Permission denied"]
            )
        
        try:
            # Soft delete
            variant.is_active = False
            variant.save()
            
            return ProductVariantDelete(
                success=True,
                errors=[]
            )
            
        except Exception as e:
            return ProductVariantDelete(
                success=False,
                errors=[f"Error deleting variant: {str(e)}"]
            )


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
            category = Category.objects.create(
                name=input.name,
                description=input.get('description'),
                parent=parent,
                is_active=input.get('is_active', True)
            )
            
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