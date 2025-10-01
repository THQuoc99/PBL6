import graphene
from django.db import transaction
from products.models import Product, ProductVariant
from ..types.product import ProductVariantType
from .bulk_product_mutations import (
    BulkProductCreate,
    BulkProductUpdate, 
    BulkProductVariantCreate,
    BulkStockUpdate,
    BulkPriceUpdate,
    BulkProductStatusUpdate,
    BulkOperationResult
)


# ===== BULK VARIANT MUTATIONS =====

class BulkVariantStatusUpdate(graphene.Mutation):
    """Bulk cập nhật trạng thái variants (active/inactive)"""
    
    class Arguments:
        variant_ids = graphene.List(graphene.Int, required=True)
        is_active = graphene.Boolean(required=True)
    
    Output = BulkOperationResult
    
    def mutate(self, info, variant_ids, is_active):
        user = info.context.user
        
        if not user.is_authenticated:
            return BulkOperationResult(
                success_count=0,
                error_count=0,
                total_count=0,
                errors=["Authentication required"],
                success=False
            )
        
        total_count = len(variant_ids)
        success_count = 0
        error_count = 0
        errors = []
        
        try:
            with transaction.atomic():
                for i, variant_id in enumerate(variant_ids):
                    try:
                        # Get variant
                        try:
                            variant = ProductVariant.objects.get(variant_id=variant_id)
                        except ProductVariant.DoesNotExist:
                            error_count += 1
                            errors.append(f"Variant {variant_id}: Not found")
                            continue
                        
                        # Check permission
                        if variant.product.seller != user and not user.is_staff:
                            error_count += 1
                            errors.append(f"Variant {variant_id}: Permission denied")
                            continue
                        
                        variant.is_active = is_active
                        variant.save()
                        
                        success_count += 1
                        
                    except Exception as e:
                        error_count += 1
                        errors.append(f"Variant {variant_id}: {str(e)}")
                
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


class BulkVariantDelete(graphene.Mutation):
    """Bulk xóa nhiều variants"""
    
    class Arguments:
        variant_ids = graphene.List(graphene.Int, required=True)
        force_delete = graphene.Boolean(default_value=False)
    
    Output = BulkOperationResult
    
    def mutate(self, info, variant_ids, force_delete=False):
        user = info.context.user
        
        if not user.is_authenticated:
            return BulkOperationResult(
                success_count=0,
                error_count=0,
                total_count=0,
                errors=["Authentication required"],
                success=False
            )
        
        total_count = len(variant_ids)
        success_count = 0
        error_count = 0
        errors = []
        
        try:
            with transaction.atomic():
                for i, variant_id in enumerate(variant_ids):
                    try:
                        # Get variant
                        try:
                            variant = ProductVariant.objects.get(variant_id=variant_id)
                        except ProductVariant.DoesNotExist:
                            error_count += 1
                            errors.append(f"Variant {variant_id}: Not found")
                            continue
                        
                        # Check permission
                        if variant.product.seller != user and not user.is_staff:
                            error_count += 1
                            errors.append(f"Variant {variant_id}: Permission denied")
                            continue
                        
                        # Check if variant has orders (if not force_delete)
                        if not force_delete and hasattr(variant, 'order_items'):
                            if variant.order_items.exists():
                                error_count += 1
                                errors.append(f"Variant {variant_id}: Has active orders, use force_delete=true")
                                continue
                        
                        variant.delete()
                        success_count += 1
                        
                    except Exception as e:
                        error_count += 1
                        errors.append(f"Variant {variant_id}: {str(e)}")
                
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


class BulkProductDelete(graphene.Mutation):
    """Bulk xóa nhiều sản phẩm"""
    
    class Arguments:
        product_ids = graphene.List(graphene.Int, required=True)
        force_delete = graphene.Boolean(default_value=False)
    
    Output = BulkOperationResult
    
    def mutate(self, info, product_ids, force_delete=False):
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
                        
                        # Check if product has orders (if not force_delete)
                        if not force_delete:
                            has_orders = any(
                                variant.order_items.exists() 
                                for variant in product.variants.all()
                                if hasattr(variant, 'order_items')
                            )
                            if has_orders:
                                error_count += 1
                                errors.append(f"Product {product_id}: Has active orders, use force_delete=true")
                                continue
                        
                        product.delete()
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


# ===== UTILITY MUTATIONS =====

class BulkStockTransfer(graphene.Mutation):
    """Transfer stock giữa các variants"""
    
    class Arguments:
        from_variant_id = graphene.Int(required=True)
        to_variant_id = graphene.Int(required=True)
        quantity = graphene.Int(required=True)
        reason = graphene.String()
    
    class Output(graphene.ObjectType):
        success = graphene.Boolean()
        from_variant = graphene.Field(ProductVariantType)
        to_variant = graphene.Field(ProductVariantType)
        errors = graphene.List(graphene.String)
    
    def mutate(self, info, from_variant_id, to_variant_id, quantity, reason=None):
        user = info.context.user
        
        if not user.is_authenticated:
            return BulkStockTransfer.Output(
                success=False,
                errors=["Authentication required"]
            )
        
        if quantity <= 0:
            return BulkStockTransfer.Output(
                success=False,
                errors=["Quantity must be positive"]
            )
        
        errors = []
        
        try:
            with transaction.atomic():
                # Get variants
                try:
                    from_variant = ProductVariant.objects.get(variant_id=from_variant_id)
                    to_variant = ProductVariant.objects.get(variant_id=to_variant_id)
                except ProductVariant.DoesNotExist:
                    return BulkStockTransfer.Output(
                        success=False,
                        errors=["One or both variants not found"]
                    )
                
                # Check permissions
                if (from_variant.product.seller != user and not user.is_staff) or \
                   (to_variant.product.seller != user and not user.is_staff):
                    return BulkStockTransfer.Output(
                        success=False,
                        errors=["Permission denied"]
                    )
                
                # Check stock availability
                if from_variant.stock < quantity:
                    return BulkStockTransfer.Output(
                        success=False,
                        errors=["Insufficient stock in source variant"]
                    )
                
                # Transfer stock
                from_variant.stock -= quantity
                to_variant.stock += quantity
                
                from_variant.save()
                to_variant.save()
                
                # TODO: Log stock transfer history
                
                return BulkStockTransfer.Output(
                    success=True,
                    from_variant=from_variant,
                    to_variant=to_variant,
                    errors=[]
                )
                
        except Exception as e:
            return BulkStockTransfer.Output(
                success=False,
                errors=[f"Transfer failed: {str(e)}"]
            )


# ===== EXPORT ALL BULK MUTATIONS =====

__all__ = [
    'BulkProductCreate',
    'BulkProductUpdate', 
    'BulkProductVariantCreate',
    'BulkStockUpdate',
    'BulkPriceUpdate',
    'BulkProductStatusUpdate',
    'BulkVariantStatusUpdate',
    'BulkVariantDelete',
    'BulkProductDelete',
    'BulkStockTransfer',
    'BulkOperationResult'
]