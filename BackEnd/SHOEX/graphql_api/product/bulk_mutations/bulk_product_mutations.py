import graphene
from graphene import InputObjectType, Mutation
from django.db import transaction
from django.core.exceptions import ValidationError
from products.models import Product, ProductVariant, Category
from ..types.product import ProductType, ProductVariantType
from ..mutations.product_mutations import ProductCreateInput, ProductVariantCreateInput


# ===== BULK INPUT TYPES =====

class BulkProductCreateInput(InputObjectType):
    """Input cho bulk tạo sản phẩm"""
    products = graphene.List(ProductCreateInput, required=True, description="Danh sách sản phẩm")


class BulkProductUpdateInput(InputObjectType):
    """Input cho bulk cập nhật sản phẩm"""
    product_id = graphene.Int(required=True)
    name = graphene.String()
    description = graphene.String()
    category_id = graphene.Int()
    base_price = graphene.Decimal()
    image_url = graphene.String()
    is_active = graphene.Boolean()


class BulkProductVariantCreateInput(InputObjectType):
    """Input cho bulk tạo biến thể"""
    variants = graphene.List(ProductVariantCreateInput, required=True, description="Danh sách biến thể")


class BulkStockUpdateInput(InputObjectType):
    """Input cho bulk cập nhật stock"""
    variant_id = graphene.Int(required=True)
    stock_change = graphene.Int(required=True)
    reason = graphene.String()


class BulkPriceUpdateInput(InputObjectType):
    """Input cho bulk cập nhật giá"""
    variant_id = graphene.Int(required=True)
    new_price = graphene.Decimal(required=True)
    reason = graphene.String()


# ===== RESULT TYPES =====

class BulkOperationResult(graphene.ObjectType):
    """Kết quả cho bulk operations"""
    success_count = graphene.Int(description="Số lượng thành công")
    error_count = graphene.Int(description="Số lượng lỗi")
    total_count = graphene.Int(description="Tổng số items")
    errors = graphene.List(graphene.String, description="Danh sách lỗi")
    success = graphene.Boolean(description="Thành công hay không")


class BulkProductCreateResult(graphene.ObjectType):
    """Kết quả bulk tạo sản phẩm"""
    success_count = graphene.Int()
    error_count = graphene.Int()
    total_count = graphene.Int()
    created_products = graphene.List(ProductType)
    errors = graphene.List(graphene.String)
    success = graphene.Boolean()


class BulkProductVariantCreateResult(graphene.ObjectType):
    """Kết quả bulk tạo biến thể"""
    success_count = graphene.Int()
    error_count = graphene.Int()
    total_count = graphene.Int()
    created_variants = graphene.List(ProductVariantType)
    errors = graphene.List(graphene.String)
    success = graphene.Boolean()


# ===== BULK MUTATIONS =====

class BulkProductCreate(Mutation):
    """Bulk tạo nhiều sản phẩm cùng lúc"""
    
    class Arguments:
        input = BulkProductCreateInput(required=True)
    
    Output = BulkProductCreateResult
    
    def mutate(self, info, input):
        user = info.context.user
        
        if not user.is_authenticated:
            return BulkProductCreateResult(
                success_count=0,
                error_count=0,
                total_count=0,
                created_products=[],
                errors=["Authentication required"],
                success=False
            )
        
        products_data = input.products
        total_count = len(products_data)
        created_products = []
        errors = []
        success_count = 0
        error_count = 0
        
        # Sử dụng database transaction
        try:
            with transaction.atomic():
                for i, product_data in enumerate(products_data):
                    try:
                        # Validate category
                        try:
                            category = Category.objects.get(
                                category_id=product_data.category_id,
                                is_active=True
                            )
                        except Category.DoesNotExist:
                            error_count += 1
                            errors.append(f"Product {i+1}: Category not found")
                            continue
                        
                        # Create product
                        product = Product.objects.create(
                            seller=user,
                            category=category,
                            name=product_data.name,
                            description=product_data.description,
                            base_price=product_data.base_price,
                            brand=product_data.get('brand'),
                            model_code=product_data.get('model_code'),
                            is_active=product_data.get('is_active', True)
                        )
                        
                        created_products.append(product)
                        success_count += 1
                        
                    except ValidationError as e:
                        error_count += 1
                        errors.append(f"Product {i+1}: {str(e)}")
                    except Exception as e:
                        error_count += 1
                        errors.append(f"Product {i+1}: {str(e)}")
                
                # Nếu có quá nhiều lỗi, rollback
                if error_count > success_count:
                    transaction.set_rollback(True)
                    return BulkProductCreateResult(
                        success_count=0,
                        error_count=total_count,
                        total_count=total_count,
                        created_products=[],
                        errors=["Too many errors, operation rolled back"] + errors,
                        success=False
                    )
                
        except Exception as e:
            return BulkProductCreateResult(
                success_count=0,
                error_count=total_count,
                total_count=total_count,
                created_products=[],
                errors=[f"Transaction failed: {str(e)}"],
                success=False
            )
        
        return BulkProductCreateResult(
            success_count=success_count,
            error_count=error_count,
            total_count=total_count,
            created_products=created_products,
            errors=errors,
            success=success_count > 0
        )


class BulkProductUpdate(Mutation):
    """Bulk cập nhật nhiều sản phẩm"""
    
    class Arguments:
        updates = graphene.List(BulkProductUpdateInput, required=True)
    
    Output = BulkOperationResult
    
    def mutate(self, info, updates):
        user = info.context.user
        
        if not user.is_authenticated:
            return BulkOperationResult(
                success_count=0,
                error_count=0,
                total_count=0,
                errors=["Authentication required"],
                success=False
            )
        
        total_count = len(updates)
        success_count = 0
        error_count = 0
        errors = []
        
        try:
            with transaction.atomic():
                for i, update_data in enumerate(updates):
                    try:
                        # Get product
                        try:
                            product = Product.objects.get(product_id=update_data.product_id)
                        except Product.DoesNotExist:
                            error_count += 1
                            errors.append(f"Update {i+1}: Product not found")
                            continue
                        
                        # Check permission
                        if product.seller != user and not user.is_staff:
                            error_count += 1
                            errors.append(f"Update {i+1}: Permission denied")
                            continue
                        
                        # Update fields
                        if update_data.get('name') is not None:
                            product.name = update_data.name
                        if update_data.get('description') is not None:
                            product.description = update_data.description
                        if update_data.get('base_price') is not None:
                            product.base_price = update_data.base_price
                        if update_data.get('brand') is not None:
                            product.brand = update_data.brand
                        if update_data.get('model_code') is not None:
                            product.model_code = update_data.model_code
                        if update_data.get('is_active') is not None:
                            product.is_active = update_data.is_active
                        
                        # Update category if provided
                        if update_data.get('category_id') is not None:
                            try:
                                category = Category.objects.get(
                                    category_id=update_data.category_id,
                                    is_active=True
                                )
                                product.category = category
                            except Category.DoesNotExist:
                                error_count += 1
                                errors.append(f"Update {i+1}: Category not found")
                                continue
                        
                        product.save()
                        success_count += 1
                        
                    except Exception as e:
                        error_count += 1
                        errors.append(f"Update {i+1}: {str(e)}")
                
        except Exception as e:
            return BulkOperationResult(
                success_count=0,
                error_count=total_count,
                total_count=total_count,
                errors=[f"Transaction failed: {str(e)}"],
                success=False
            )
        
        return BulkOperationResult(
            success_count=success_count,
            error_count=error_count,
            total_count=total_count,
            errors=errors,
            success=success_count > 0
        )


class BulkProductVariantCreate(Mutation):
    """Bulk tạo nhiều biến thể"""
    
    class Arguments:
        input = BulkProductVariantCreateInput(required=True)
    
    Output = BulkProductVariantCreateResult
    
    def mutate(self, info, input):
        user = info.context.user
        
        if not user.is_authenticated:
            return BulkProductVariantCreateResult(
                success_count=0,
                error_count=0,
                total_count=0,
                created_variants=[],
                errors=["Authentication required"],
                success=False
            )
        
        variants_data = input.variants
        total_count = len(variants_data)
        created_variants = []
        errors = []
        success_count = 0
        error_count = 0
        
        try:
            with transaction.atomic():
                for i, variant_data in enumerate(variants_data):
                    try:
                        # Validate product
                        try:
                            product = Product.objects.get(product_id=variant_data.product_id)
                        except Product.DoesNotExist:
                            error_count += 1
                            errors.append(f"Variant {i+1}: Product not found")
                            continue
                        
                        # Check permission
                        if product.seller != user and not user.is_staff:
                            error_count += 1
                            errors.append(f"Variant {i+1}: Permission denied")
                            continue
                        
                        # Check SKU unique
                        if ProductVariant.objects.filter(sku=variant_data.sku).exists():
                            error_count += 1
                            errors.append(f"Variant {i+1}: SKU already exists")
                            continue
                        
                        # Create variant
                        variant = ProductVariant.objects.create(
                            product=product,
                            sku=variant_data.sku,
                            price=variant_data.price,
                            stock=variant_data.stock,
                            weight=variant_data.get('weight', 0.1),
                            image_url=variant_data.get('image_url'),
                            option_combinations=variant_data.get('option_combinations', {}),
                            is_active=variant_data.get('is_active', True)
                        )
                        
                        created_variants.append(variant)
                        success_count += 1
                        
                    except ValidationError as e:
                        error_count += 1
                        errors.append(f"Variant {i+1}: {str(e)}")
                    except Exception as e:
                        error_count += 1
                        errors.append(f"Variant {i+1}: {str(e)}")
                
        except Exception as e:
            return BulkProductVariantCreateResult(
                success_count=0,
                error_count=total_count,
                total_count=total_count,
                created_variants=[],
                errors=[f"Transaction failed: {str(e)}"],
                success=False
            )
        
        return BulkProductVariantCreateResult(
            success_count=success_count,
            error_count=error_count,
            total_count=total_count,
            created_variants=created_variants,
            errors=errors,
            success=success_count > 0
        )


class BulkStockUpdate(Mutation):
    """Bulk cập nhật tồn kho nhiều variants"""
    
    class Arguments:
        updates = graphene.List(BulkStockUpdateInput, required=True)
    
    Output = BulkOperationResult
    
    def mutate(self, info, updates):
        user = info.context.user
        
        if not user.is_authenticated:
            return BulkOperationResult(
                success_count=0,
                error_count=0,
                total_count=0,
                errors=["Authentication required"],
                success=False
            )
        
        total_count = len(updates)
        success_count = 0
        error_count = 0
        errors = []
        
        try:
            with transaction.atomic():
                for i, update_data in enumerate(updates):
                    try:
                        # Get variant
                        try:
                            variant = ProductVariant.objects.get(variant_id=update_data.variant_id)
                        except ProductVariant.DoesNotExist:
                            error_count += 1
                            errors.append(f"Stock update {i+1}: Variant not found")
                            continue
                        
                        # Check permission
                        if variant.product.seller != user and not user.is_staff:
                            error_count += 1
                            errors.append(f"Stock update {i+1}: Permission denied")
                            continue
                        
                        # Calculate new stock
                        new_stock = variant.stock + update_data.stock_change
                        
                        if new_stock < 0:
                            error_count += 1
                            errors.append(f"Stock update {i+1}: Stock cannot be negative")
                            continue
                        
                        variant.stock = new_stock
                        variant.save()
                        
                        # TODO: Log stock history
                        
                        success_count += 1
                        
                    except Exception as e:
                        error_count += 1
                        errors.append(f"Stock update {i+1}: {str(e)}")
                
        except Exception as e:
            return BulkOperationResult(
                success_count=0,
                error_count=total_count,
                total_count=total_count,
                errors=[f"Transaction failed: {str(e)}"],
                success=False
            )
        
        return BulkOperationResult(
            success_count=success_count,
            error_count=error_count,
            total_count=total_count,
            errors=errors,
            success=success_count > 0
        )


class BulkPriceUpdate(Mutation):
    """Bulk cập nhật giá nhiều variants"""
    
    class Arguments:
        updates = graphene.List(BulkPriceUpdateInput, required=True)
    
    Output = BulkOperationResult
    
    def mutate(self, info, updates):
        user = info.context.user
        
        if not user.is_authenticated:
            return BulkOperationResult(
                success_count=0,
                error_count=0,
                total_count=0,
                errors=["Authentication required"],
                success=False
            )
        
        total_count = len(updates)
        success_count = 0
        error_count = 0
        errors = []
        
        try:
            with transaction.atomic():
                for i, update_data in enumerate(updates):
                    try:
                        # Get variant
                        try:
                            variant = ProductVariant.objects.get(variant_id=update_data.variant_id)
                        except ProductVariant.DoesNotExist:
                            error_count += 1
                            errors.append(f"Price update {i+1}: Variant not found")
                            continue
                        
                        # Check permission
                        if variant.product.seller != user and not user.is_staff:
                            error_count += 1
                            errors.append(f"Price update {i+1}: Permission denied")
                            continue
                        
                        # Validate price
                        if update_data.new_price <= 0:
                            error_count += 1
                            errors.append(f"Price update {i+1}: Price must be positive")
                            continue
                        
                        variant.price = update_data.new_price
                        variant.save()
                        
                        # TODO: Log price history
                        
                        success_count += 1
                        
                    except Exception as e:
                        error_count += 1
                        errors.append(f"Price update {i+1}: {str(e)}")
                
        except Exception as e:
            return BulkOperationResult(
                success_count=0,
                error_count=total_count,
                total_count=total_count,
                errors=[f"Transaction failed: {str(e)}"],
                success=False
            )
        
        return BulkOperationResult(
            success_count=success_count,
            error_count=error_count,
            total_count=total_count,
            errors=errors,
            success=success_count > 0
        )


class BulkProductStatusUpdate(Mutation):
    """Bulk cập nhật trạng thái sản phẩm (active/inactive)"""
    
    class Arguments:
        product_ids = graphene.List(graphene.Int, required=True)
        is_active = graphene.Boolean(required=True)
    
    Output = BulkOperationResult
    
    def mutate(self, info, product_ids, is_active):
        user = info.context.user
        
        if not user.is_authenticated:
            return BulkOperationResult(
                success_count=0,
                error_count=0,
                total_count=0,
                errors=["Authentication required"],
                success=False
            )
        
        total_count = len(product_ids)
        success_count = 0
        error_count = 0
        errors = []
        
        try:
            with transaction.atomic():
                for i, product_id in enumerate(product_ids):
                    try:
                        # Get product
                        try:
                            product = Product.objects.get(product_id=product_id)
                        except Product.DoesNotExist:
                            error_count += 1
                            errors.append(f"Product {product_id}: Not found")
                            continue
                        
                        # Check permission
                        if product.seller != user and not user.is_staff:
                            error_count += 1
                            errors.append(f"Product {product_id}: Permission denied")
                            continue
                        
                        product.is_active = is_active
                        product.save()
                        
                        # Also update variants status
                        product.variants.update(is_active=is_active)
                        
                        success_count += 1
                        
                    except Exception as e:
                        error_count += 1
                        errors.append(f"Product {product_id}: {str(e)}")
                
        except Exception as e:
            return BulkOperationResult(
                success_count=0,
                error_count=total_count,
                total_count=total_count,
                errors=[f"Transaction failed: {str(e)}"],
                success=False
            )
        
        return BulkOperationResult(
            success_count=success_count,
            error_count=error_count,
            total_count=total_count,
            errors=errors,
            success=success_count > 0
        )