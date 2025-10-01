from collections import defaultdict
from promise import Promise
from promise.dataloader import DataLoader
from products.models import Product, Category, ProductVariant, ProductAttribute, ProductAttributeOption, ProductImage


class CategoryByIdLoader(DataLoader):
    """
    DataLoader để load Category theo ID
    Tối ưu cho việc load category của nhiều products cùng lúc
    """
    def batch_load_fn(self, category_ids):
        # Lấy tất cả categories trong 1 query
        categories = Category.objects.filter(
            category_id__in=category_ids
        ).in_bulk(field_name='category_id')
        
        # Trả về theo đúng thứ tự của category_ids
        return Promise.resolve([
            categories.get(category_id) for category_id in category_ids
        ])


class ProductByIdLoader(DataLoader):
    """
    DataLoader để load Product theo ID
    """
    def batch_load_fn(self, product_ids):
        products = Product.objects.filter(
            product_id__in=product_ids
        ).select_related('seller', 'category').in_bulk(field_name='product_id')
        
        return Promise.resolve([
            products.get(product_id) for product_id in product_ids
        ])


class ProductsByCategoryIdLoader(DataLoader):
    """
    DataLoader để load Products theo Category ID
    Dùng cho resolver products của Category
    """
    def batch_load_fn(self, category_ids):
        # Query tất cả products của các categories
        products = Product.objects.filter(
            category_id__in=category_ids,
            is_active=True
        ).select_related('seller', 'category')
        
        # Nhóm products theo category_id
        products_by_category = defaultdict(list)
        for product in products:
            products_by_category[product.category_id].append(product)
        
        # Trả về theo đúng thứ tự category_ids
        return Promise.resolve([
            products_by_category[category_id] for category_id in category_ids
        ])


class ProductVariantsByProductIdLoader(DataLoader):
    """
    DataLoader để load ProductVariants theo Product ID
    Tối ưu cho việc load variants của nhiều products
    """
    def batch_load_fn(self, product_ids):
        variants = ProductVariant.objects.filter(
            product_id__in=product_ids,
            is_active=True
        ).select_related('product')
        
        # Nhóm variants theo product_id
        variants_by_product = defaultdict(list)
        for variant in variants:
            variants_by_product[variant.product_id].append(variant)
        
        return Promise.resolve([
            variants_by_product[product_id] for product_id in product_ids
        ])


class ProductVariantByIdLoader(DataLoader):
    """
    DataLoader để load ProductVariant theo ID
    """
    def batch_load_fn(self, variant_ids):
        variants = ProductVariant.objects.filter(
            variant_id__in=variant_ids
        ).select_related('product').in_bulk(field_name='variant_id')
        
        return Promise.resolve([
            variants.get(variant_id) for variant_id in variant_ids
        ])


class ProductAttributeOptionsByProductIdLoader(DataLoader):
    """
    DataLoader để load ProductAttributeOptions theo Product ID
    Dùng để lấy các tùy chọn thuộc tính của sản phẩm
    """
    def batch_load_fn(self, product_ids):
        options = ProductAttributeOption.objects.filter(
            attribute__product_id__in=product_ids
        ).select_related('attribute').order_by('attribute__display_order', 'display_order')
        
        # Nhóm options theo product_id
        options_by_product = defaultdict(list)
        for option in options:
            product_id = option.attribute.product_id
            options_by_product[product_id].append(option)
        
        return Promise.resolve([
            options_by_product[product_id] for product_id in product_ids
        ])


class ProductAttributeByIdLoader(DataLoader):
    """
    DataLoader để load ProductAttribute theo ID
    """
    def batch_load_fn(self, attribute_ids):
        attributes = ProductAttribute.objects.filter(
            attribute_id__in=attribute_ids
        ).in_bulk(field_name='attribute_id')
        
        return Promise.resolve([
            attributes.get(attribute_id) for attribute_id in attribute_ids
        ])


class ProductImagesByProductIdLoader(DataLoader):
    """
    DataLoader để load ProductImages theo Product ID
    Dùng để lấy gallery images của sản phẩm
    """
    def batch_load_fn(self, product_ids):
        images = ProductImage.objects.filter(
            product_id__in=product_ids
        ).order_by('display_order', 'image_id')
        
        # Nhóm images theo product_id
        images_by_product = defaultdict(list)
        for image in images:
            images_by_product[image.product_id].append(image)
        
        return Promise.resolve([
            images_by_product[product_id] for product_id in product_ids
        ])


class SubcategoriesByCategoryIdLoader(DataLoader):
    """
    DataLoader để load subcategories theo Category ID
    Dùng cho category tree
    """
    def batch_load_fn(self, category_ids):
        subcategories = Category.objects.filter(
            parent_id__in=category_ids,
            is_active=True
        )
        
        # Nhóm subcategories theo parent_id
        subcategories_by_parent = defaultdict(list)
        for subcategory in subcategories:
            subcategories_by_parent[subcategory.parent_id].append(subcategory)
        
        return Promise.resolve([
            subcategories_by_parent[category_id] for category_id in category_ids
        ])


class SellerByIdLoader(DataLoader):
    """
    DataLoader để load User (Seller) theo ID
    Tối ưu cho việc load thông tin người bán
    """
    def batch_load_fn(self, seller_ids):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        sellers = User.objects.filter(
            id__in=seller_ids
        ).in_bulk()
        
        return Promise.resolve([
            sellers.get(seller_id) for seller_id in seller_ids
        ])


# ===== AGGREGATE DATALOADERS =====

class ProductStockByProductIdLoader(DataLoader):
    """
    DataLoader để tính tổng stock theo Product ID
    Tối ưu cho resolve_total_stock
    """
    def batch_load_fn(self, product_ids):
        from django.db.models import Sum
        
        # Query stock tổng theo product
        stock_data = ProductVariant.objects.filter(
            product_id__in=product_ids,
            is_active=True
        ).values('product_id').annotate(
            total_stock=Sum('stock')
        )
        
        # Tạo mapping
        stock_by_product = {
            item['product_id']: item['total_stock'] or 0 
            for item in stock_data
        }
        
        return Promise.resolve([
            stock_by_product.get(product_id, 0) for product_id in product_ids
        ])


class ProductPriceRangeByProductIdLoader(DataLoader):
    """
    DataLoader để tính price range theo Product ID
    Tối ưu cho resolve_min_price, resolve_max_price
    """
    def batch_load_fn(self, product_ids):
        from django.db.models import Min, Max
        
        # Query price range theo product
        price_data = ProductVariant.objects.filter(
            product_id__in=product_ids,
            is_active=True
        ).values('product_id').annotate(
            min_price=Min('price'),
            max_price=Max('price')
        )
        
        # Tạo mapping
        price_ranges = {}
        for item in price_data:
            price_ranges[item['product_id']] = {
                'min': item['min_price'],
                'max': item['max_price']
            }
        
        return Promise.resolve([
            price_ranges.get(product_id, {'min': 0, 'max': 0}) 
            for product_id in product_ids
        ])


class ProductsBySellerLoader(DataLoader):
    """
    DataLoader để load Products theo Seller ID
    Tối ưu cho queries liên quan đến seller
    """
    def batch_load_fn(self, seller_ids):
        products_by_seller = {}
        
        # Query products theo seller
        products = Product.objects.filter(
            seller_id__in=seller_ids,
            is_active=True
        ).select_related('category')
        
        # Group theo seller_id
        for product in products:
            if product.seller_id not in products_by_seller:
                products_by_seller[product.seller_id] = []
            products_by_seller[product.seller_id].append(product)
        
        return Promise.resolve([
            products_by_seller.get(seller_id, []) 
            for seller_id in seller_ids
        ])


class ProductVariantsByProductLoader(DataLoader):
    """
    DataLoader để load ProductVariants theo Product ID
    Alias cho ProductVariantsByProductIdLoader
    """
    def batch_load_fn(self, product_ids):
        variants_by_product = {}
        
        # Query variants theo product
        variants = ProductVariant.objects.filter(
            product_id__in=product_ids,
            is_active=True
        ).select_related('product')
        
        # Group theo product_id
        for variant in variants:
            if variant.product_id not in variants_by_product:
                variants_by_product[variant.product_id] = []
            variants_by_product[variant.product_id].append(variant)
        
        return Promise.resolve([
            variants_by_product.get(product_id, []) 
            for product_id in product_ids
        ])


# ===== HELPER FUNCTIONS =====

def get_dataloader_context():
    """
    Tạo context chứa tất cả dataloaders
    Sử dụng trong GraphQL context
    """
    return {
        'category_by_id_loader': CategoryByIdLoader(),
        'product_by_id_loader': ProductByIdLoader(),
        'products_by_category_id_loader': ProductsByCategoryIdLoader(),
        'products_by_seller_loader': ProductsBySellerLoader(),
        'product_variants_by_product_id_loader': ProductVariantsByProductIdLoader(),
        'product_variants_by_product_loader': ProductVariantsByProductLoader(),
        'product_variant_by_id_loader': ProductVariantByIdLoader(),
        'product_attribute_options_by_product_id_loader': ProductAttributeOptionsByProductIdLoader(),
        'product_attribute_by_id_loader': ProductAttributeByIdLoader(),
        'product_images_by_product_id_loader': ProductImagesByProductIdLoader(),
        'subcategories_by_category_id_loader': SubcategoriesByCategoryIdLoader(),
        'seller_by_id_loader': SellerByIdLoader(),
        'product_stock_by_product_id_loader': ProductStockByProductIdLoader(),
        'product_price_range_by_product_id_loader': ProductPriceRangeByProductIdLoader(),
    }