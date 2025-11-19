# Bulk mutations package
from .bulk_product_mutations import (
    BulkProductCreate,
    BulkProductUpdate, 
    BulkProductVariantCreate,
    BulkStockUpdate,
    BulkPriceUpdate,
    BulkProductStatusUpdate,
    BulkOperationResult
)

from .bulk_variants_mutations import (
    BulkVariantStatusUpdate,
    BulkVariantDelete,
    BulkProductDelete,
    BulkStockTransfer
)

__all__ = [
    # Product bulk operations
    'BulkProductCreate',
    'BulkProductUpdate', 
    'BulkProductVariantCreate',
    'BulkStockUpdate',
    'BulkPriceUpdate',
    'BulkProductStatusUpdate',
    
    # Variant bulk operations
    'BulkVariantStatusUpdate',
    'BulkVariantDelete',
    'BulkProductDelete',
    'BulkStockTransfer',
    
    # Result types
    'BulkOperationResult'
]