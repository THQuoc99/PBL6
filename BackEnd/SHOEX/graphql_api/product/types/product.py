from discount.models import Voucher
import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from products.models import (
    Product, Category, ProductVariant, 
    ProductAttribute, ProductAttributeOption,
    ProductImage
)
from brand.models import Brand
    
from .utils import get_max_discount
from django.db.models import Q, Max
from django.utils import timezone
from decimal import Decimal
class BrandType(DjangoObjectType):
    class Meta:
        model = Brand
        fields = "__all__"

class CategoryType(DjangoObjectType):
    """Danh mục sản phẩm - Cây phân cấp"""
    class Meta:
        model = Category
        fields = '__all__'
        interfaces = (relay.Node,)

    # Thêm các trường tùy chỉnh
    product_count = graphene.Int(description="Số lượng sản phẩm trong danh mục")
    thumbnail_image = graphene.String(description="Hình ảnh đại diện danh mục")
    full_path = graphene.List(lambda: CategoryType, description="Đường dẫn đầy đủ của danh mục")
    
    # Explicitly define subcategories field to ensure it works
    subcategories = graphene.List(lambda: CategoryType, description="Danh mục con")
    
    def resolve_product_count(self, info):
        """Đếm số lượng sản phẩm active trong danh mục"""
        return self.products.filter(is_active=True).count()
    
    def resolve_thumbnail_image(self, info):
        """Lấy ảnh đại diện của danh mục"""
        # Ưu tiên: Ảnh thumbnail riêng của category
        if self.thumbnail_image and hasattr(self.thumbnail_image, 'url'):
            return self.thumbnail_image.url
        
        # Fallback 1: Lấy từ sản phẩm nổi bật đầu tiên
        first_product = self.products.filter(
            is_active=True, 
            is_featured=True
        ).first()
        
        if first_product:
            thumbnail = first_product.gallery_images.filter(is_thumbnail=True).first()
            if thumbnail and thumbnail.image and hasattr(thumbnail.image, 'url'):
                return thumbnail.image.url
        
        # Fallback 2: Lấy từ sản phẩm active bất kỳ
        any_product = self.products.filter(is_active=True).first()
        if any_product:
            thumbnail = any_product.gallery_images.filter(is_thumbnail=True).first()
            if thumbnail and thumbnail.image and hasattr(thumbnail.image, 'url'):
                return thumbnail.image.url
        
        # Không có ảnh nào
        return None
    
    def resolve_full_path(self, info):
        path = [self]  # bắt đầu từ chính category hiện tại
        parent = self.parent
        while parent:
            path.insert(0, parent)  # chèn parent lên đầu danh sách
            parent = parent.parent
        return path
    def resolve_subcategories(self, info):
        """Resolve subcategories - danh mục con"""
        return self.subcategories.filter(is_active=True).order_by('name')


class ProductImageType(DjangoObjectType):
    """Ảnh chung của sản phẩm (đại diện + gallery)"""
    class Meta:
        model = ProductImage
        fields = '__all__'
        interfaces = (relay.Node,)
    
    # Thêm field tùy chỉnh để trả về URL ảnh
    image_url = graphene.String(description="URL của ảnh")
    
    def resolve_image_url(self, info):
        """Trả về URL của ảnh"""
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return None


class ProductAttributeType(DjangoObjectType):
    """Thuộc tính sản phẩm (Size, Color, Material...)"""
    class Meta:
        model = ProductAttribute
        fields = '__all__'
        interfaces = (relay.Node,)
    
    # Thêm thông tin bổ sung
    option_count = graphene.Int(description="Số lượng tùy chọn có sẵn")
    
    def resolve_option_count(self, info):
        """Đếm số lượng tùy chọn của thuộc tính này"""
        return self.product_options.filter(is_available=True).count()


class ProductAttributeOptionType(DjangoObjectType):
    """Tùy chọn thuộc tính sản phẩm với hình ảnh"""
    class Meta:
        model = ProductAttributeOption
        fields = '__all__'
        interfaces = (relay.Node,)
    
    # Thêm field tùy chỉnh để trả về URL ảnh
    image_url = graphene.String(description="URL của ảnh tùy chọn")
    
    def resolve_image_url(self, info):
        """Trả về URL của ảnh tùy chọn"""
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return None
    
    # Thêm thông tin động
    variant_count = graphene.Int(description="Số variants có tùy chọn này")
    available_combinations = graphene.JSONString(description="Các kết hợp có sẵn")
    
    def resolve_variant_count(self, info):
        """Đếm số variants có tùy chọn này"""
        return self.get_variants().count()
    
    def resolve_available_combinations(self, info):
        """Lấy các kết hợp khác có sẵn khi chọn tùy chọn này"""
        return self.get_available_combinations()


class ProductVariantType(DjangoObjectType):
    """Biến thể sản phẩm - SKU cụ thể"""
    class Meta:
        model = ProductVariant
        fields = '__all__'
        interfaces = (relay.Node,)
    
    # ===== THÔNG TIN CƠ BẢN =====
    is_in_stock = graphene.Boolean(description="Còn hàng hay không")
    discount_percentage = graphene.Float(description="Phần trăm giảm giá")
    original_price = graphene.Decimal(description="Giá gốc")
    final_price = graphene.Decimal(description="Giá cuối cùng")
    
    # ===== THÔNG TIN THUỘC TÍNH =====
    color_name = graphene.String(description="Tên màu sắc")
    size_name = graphene.String(description="Kích thước")
    color_image_url = graphene.String(description="Ảnh màu sắc")
    
    # ===== TRẠNG THÁI =====
    stock_status = graphene.String(description="Trạng thái kho")
    
    def resolve_is_in_stock(self, info):
        """Kiểm tra còn hàng"""
        return self.is_in_stock
    def resolve_discount_percentage(self, info):
        # Lấy object product
        product = self.product
        # Gọi resolver discount của ProductType
        discount = get_max_discount(product)
        return discount

    def resolve_final_price(self, info):
        discount = Decimal(get_max_discount(self.product))  # convert float -> Decimal
        return self.price * (Decimal('1.0') - discount / Decimal('100.0'))
    
    def resolve_color_name(self, info):
        """Lấy tên màu từ option_combinations"""
        return self.color_name
    
    def resolve_size_name(self, info):
        """Lấy size từ option_combinations"""
        return self.size_name
    
    def resolve_color_image_url(self, info):
        """Lấy ảnh màu tương ứng"""
        color_image = self.color_image
        if color_image and color_image.image and hasattr(color_image.image, 'url'):
            return color_image.image.url
        return None
    
    def resolve_stock_status(self, info):
        """Trạng thái kho hàng"""
        if self.stock <= 0:
            return "out_of_stock"
        elif self.stock <= 5:
            return "low_stock"
        elif self.stock <= 20:
            return "medium_stock"
        else:
            return "in_stock"


class ProductType(DjangoObjectType):
    """Sản phẩm chính - Thiết kế theo Shopee/TikTok/Lazada"""
    class Meta:
        model = Product
        fields = '__all__'
        interfaces = (relay.Node,)
    
    # ===== GIÁ CẢ & KHUYẾN MÃI =====
    price_range = graphene.String(description="Khoảng giá")
    min_price = graphene.Decimal(description="Giá thấp nhất")
    max_price = graphene.Decimal(description="Giá cao nhất")
    discount_percentage = graphene.Float(description="% giảm giá cao nhất")
    final_price = graphene.Decimal(description="Giá cuối cùng")
    has_discount = graphene.Boolean(description="Có giảm giá không")
    is_new=graphene.Boolean(description="Sản phẩm mới")
    is_hot=graphene.Boolean(description="Sản phẩm bán chạy")
    # ===== HÌNH ẢNH THEO MODEL MỚI =====
    gallery_images = graphene.List(ProductImageType, description="Ảnh gallery sản phẩm")
    thumbnail_image = graphene.Field(ProductImageType, description="Ảnh đại diện")
    color_images = graphene.List(ProductAttributeOptionType, description="Ảnh theo màu sắc")
    
    # ===== THUỘC TÍNH & TÙY CHỌN =====
    attribute_options = graphene.List(ProductAttributeOptionType, description="Tất cả tùy chọn thuộc tính")
    available_attributes = graphene.List(ProductAttributeType, description="Các thuộc tính có sẵn")
    color_options = graphene.List(ProductAttributeOptionType, description="Tùy chọn màu sắc")
    size_options = graphene.List(ProductAttributeOptionType, description="Tùy chọn kích thước")
    
    # ===== THỐNG KÊ =====
    total_sold = graphene.Int(description="Tổng số đã bán")
    total_stock = graphene.Int(description="Tổng tồn kho")
    variant_count = graphene.Int(description="Số lượng biến thể")
    available_colors_count = graphene.Int(description="Số màu có sẵn")
    
    # ===== ĐÁNH GIÁ =====
    rating_average = graphene.Float(description="Điểm đánh giá trung bình")
    review_count = graphene.Int(description="Số lượng đánh giá")
    
    # ===== TRẠNG THÁI =====
    availability_status = graphene.String(description="Trạng thái hàng")
    
    # ===== THÔNG TIN BỔ SUNG =====
    tags = graphene.List(graphene.String, description="Tags sản phẩm")
    shipping_info = graphene.String(description="Thông tin vận chuyển")
    warranty_info = graphene.String(description="Thông tin bảo hành")
    
    # ===== RESOLVERS =====
    def resolve_is_new(self, info):
        return self.is_new
    def resolve_is_hot(self, info):
        return self.is_hot
    
    def resolve_price_range(self, info):
        """Khoảng giá từ variants"""
        min_p, max_p = self.min_price, self.max_price
        if min_p == max_p:
            return f"{min_p:,.0f}đ"
        return f"{min_p:,.0f}đ - {max_p:,.0f}đ"
    
    def resolve_min_price(self, info):
        """Giá thấp nhất (sử dụng property từ model)"""
        return self.min_price
    
    def resolve_max_price(self, info):
        """Giá cao nhất (sử dụng property từ model)"""
        return self.max_price


    def resolve_discount_percentage(self, info):
        return get_max_discount(self)

    def resolve_final_price(self, info):
        discount = Decimal(get_max_discount(self))  # convert float -> Decimal
        return self.base_price * (Decimal('1.0') - discount / Decimal('100.0'))

    def resolve_has_discount(self, info):
        """Có giảm giá không"""
        # Always use the resolver for discount_percentage, not a model attribute
        discount = None
        # Try to use the resolver if present
        if hasattr(self, 'resolve_discount_percentage'):
            discount = self.resolve_discount_percentage(info)
        elif hasattr(self, 'discount_percentage'):
            discount = self.discount_percentage
        else:
            discount = 0.0
        return discount > 0
    
    # ===== HÌNH ẢNH THEO MODEL MỚI =====
    def resolve_gallery_images(self, info):
        """Tất cả ảnh gallery"""
        return self.gallery_images.all()
    
    def resolve_thumbnail_image(self, info):
        """Ảnh đại diện"""
        return self.gallery_images.filter(is_thumbnail=True).first()
    
    def resolve_color_images(self, info):
        """Ảnh theo màu sắc"""
        return self.attribute_options.filter(
            attribute__has_image=True,
            is_available=True
        )
    
    # ===== THUỘC TÍNH & TÙY CHỌN =====
    def resolve_attribute_options(self, info):
        """Tất cả tùy chọn thuộc tính"""
        return self.attribute_options.filter(is_available=True)
    
    def resolve_available_attributes(self, info):
        """Các thuộc tính có sẵn"""
        attribute_ids = self.attribute_options.filter(
            is_available=True
        ).values_list('attribute_id', flat=True).distinct()
        return ProductAttribute.objects.filter(attribute_id__in=attribute_ids)
    
    def resolve_color_options(self, info):
        """Tùy chọn màu sắc"""
        return self.attribute_options.filter(
            attribute__name='Color',
            is_available=True
        )
    
    def resolve_size_options(self, info):
        """Tùy chọn kích thước"""
        return self.attribute_options.filter(
            attribute__name='Size',
            is_available=True
        )
    
    # ===== THỐNG KÊ =====
    def resolve_total_sold(self, info):
        return self.sold_count
    
    def resolve_total_stock(self, info):
        """Tổng tồn kho (sử dụng property từ model)"""
        return self.total_stock
    
    def resolve_variant_count(self, info):
        """Số lượng biến thể"""
        return self.variants.filter(is_active=True).count()
    
    def resolve_available_colors_count(self, info):
        """Số màu có sẵn"""
        return self.attribute_options.filter(
            attribute__name='Color',
            is_available=True
        ).count()
    
    # ===== ĐÁNH GIÁ =====
    def resolve_rating_average(self, info):
        """Điểm đánh giá trung bình - TODO: tích hợp review system"""
        return self.rating  # Mock data
    
    def resolve_review_count(self, info):
        """Số lượng đánh giá - TODO: tích hợp review system"""
        return self.review_count  # Mock data
    
    # ===== TRẠNG THÁI =====
    def resolve_availability_status(self, info):
        """Trạng thái hàng"""
        total_stock = self.total_stock
        if total_stock > 0:
            return "in_stock"
        elif self.variants.filter(is_active=True).exists():
            return "out_of_stock"
        else:
            return "unavailable"
    
    # ===== THÔNG TIN BỔ SUNG =====
    def resolve_tags(self, info):
        """Tags sản phẩm"""
        tags = [self.category.name, self.brand.name] if self.brand else [self.category.name]
        # Thêm tags từ attributes
        attributes = self.resolve_available_attributes(info)
        for attr in attributes:
            tags.append(attr.name)
        
        return list(set(tags))  # Loại bỏ trùng lặp
    
    def resolve_shipping_info(self, info):
        """Thông tin vận chuyển"""
        return "Miễn phí vận chuyển cho đơn hàng trên 200.000đ"
    
    def resolve_warranty_info(self, info):
        """Thông tin bảo hành"""
        return "Bảo hành 6 tháng từ nhà sản xuất"


# ===== INPUT TYPES FOR MUTATIONS =====

class ProductImageInput(graphene.InputObjectType):
    """Input cho ảnh sản phẩm"""
    image_url = graphene.String(required=True)
    is_thumbnail = graphene.Boolean(default_value=False)
    alt_text = graphene.String()
    display_order = graphene.Int(default_value=0)


class ProductAttributeOptionInput(graphene.InputObjectType):
    """Input cho tùy chọn thuộc tính"""
    attribute_name = graphene.String(required=True)
    value = graphene.String(required=True)
    value_code = graphene.String()
    image_url = graphene.String()
    display_order = graphene.Int(default_value=0)


class ProductVariantInput(graphene.InputObjectType):
    """Input cho variant sản phẩm"""
    sku = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int(default_value=0)
    weight = graphene.Decimal(default_value=0.1)
    option_combinations = graphene.JSONString(required=True)


class CreateProductInput(graphene.InputObjectType):
    """Input cho tạo sản phẩm mới"""
    category_id = graphene.ID(required=True)
    name = graphene.String(required=True)
    description = graphene.String(required=True)
    base_price = graphene.Decimal(required=True)
    brand_id = graphene.ID(description="ID thương hiệu")
    model_code = graphene.String()
    is_featured = graphene.Boolean(default_value=False)
    
    # Ảnh sản phẩm
    gallery_images = graphene.List(ProductImageInput)
    
    # Tùy chọn thuộc tính
    attribute_options = graphene.List(ProductAttributeOptionInput)
    
    # Variants
    variants = graphene.List(ProductVariantInput)


# ===== MUTATIONS =====

class CreateProduct(graphene.Mutation):
    """Tạo sản phẩm mới với đầy đủ thông tin"""
    
    class Arguments:
        input = CreateProductInput(required=True)
    
    product = graphene.Field(ProductType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)
    
    @staticmethod
    def mutate(root, info, input):
        try:
            # Tạo sản phẩm chính
            product = Product.objects.create(
                seller=info.context.user,  # Lấy từ context
                category_id=input.category_id,
                name=input.name,
                description=input.description,
                base_price=input.base_price,
                brand_id=input.get('brand_id'),
                model_code=input.get('model_code'),
                is_featured=input.get('is_featured', False)
            )
            
            # Tạo ảnh gallery
            if input.get('gallery_images'):
                for img_input in input.gallery_images:
                    ProductImage.objects.create(
                        product=product,
                        image_url=img_input.image_url,
                        is_thumbnail=img_input.get('is_thumbnail', False),
                        alt_text=img_input.get('alt_text'),
                        display_order=img_input.get('display_order', 0)
                    )
            
            # Tạo attribute options
            if input.get('attribute_options'):
                for option_input in input.attribute_options:
                    # Lấy hoặc tạo attribute
                    attribute, _ = ProductAttribute.objects.get_or_create(
                        name=option_input.attribute_name,
                        defaults={
                            'type': 'color' if option_input.get('image_url') else 'select',
                            'has_image': bool(option_input.get('image_url'))
                        }
                    )
                    
                    # Tạo option
                    ProductAttributeOption.objects.create(
                        product=product,
                        attribute=attribute,
                        value=option_input.value,
                        value_code=option_input.get('value_code'),
                        image_url=option_input.get('image_url'),
                        display_order=option_input.get('display_order', 0)
                    )
            
            # Tạo variants
            if input.get('variants'):
                for variant_input in input.variants:
                    ProductVariant.objects.create(
                        product=product,
                        sku=variant_input.sku,
                        price=variant_input.price,
                        stock=variant_input.get('stock', 0),
                        weight=variant_input.get('weight', 0.1),
                        option_combinations=variant_input.option_combinations
                    )
            
            return CreateProduct(
                product=product,
                success=True,
                errors=[]
            )
            
        except Exception as e:
            return CreateProduct(
                product=None,
                success=False,
                errors=[str(e)]
            )


# ===== CONNECTION TYPES =====

class ProductConnection(relay.Connection):
    class Meta:
        node = ProductType

class ProductCountableConnection(relay.Connection):
    class Meta:
        node = ProductType

class CategoryConnection(relay.Connection):
    class Meta:
        node = CategoryType

class CategoryCountableConnection(relay.Connection):
    class Meta:
        node = CategoryType

class ProductVariantConnection(relay.Connection):
    class Meta:
        node = ProductVariantType

class ProductVariantCountableConnection(relay.Connection):
    class Meta:
        node = ProductVariantType
