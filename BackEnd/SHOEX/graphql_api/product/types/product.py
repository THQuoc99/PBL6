import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from products.models import (
    Product, Category, ProductVariant, 
    ProductAttribute, ProductAttributeOption,
    ProductImage
)


class CategoryType(DjangoObjectType):
    """Danh mục sản phẩm - Cây phân cấp"""
    class Meta:
        model = Category
        fields = '__all__'
        interfaces = (relay.Node,)

    # Thêm các trường tùy chỉnh
    product_count = graphene.Int(description="Số lượng sản phẩm trong danh mục")
    thumbnail_image = graphene.String(description="Hình ảnh đại diện danh mục")
    full_path = graphene.String(description="Đường dẫn đầy đủ của danh mục")
    
    def resolve_product_count(self, info):
        """Đếm số lượng sản phẩm active trong danh mục"""
        return self.products.filter(is_active=True).count()
    
    def resolve_thumbnail_image(self, info):
        """Lấy ảnh đại diện từ sản phẩm nổi bật đầu tiên"""
        first_product = self.products.filter(
            is_active=True, 
            is_featured=True
        ).first()
        
        if first_product:
            thumbnail = first_product.gallery_images.filter(is_thumbnail=True).first()
            return thumbnail.image_url if thumbnail else None
        return None
    
    def resolve_full_path(self, info):
        """Đường dẫn đầy đủ: Thời trang > Giày dép > Giày thể thao"""
        path = [self.name]
        parent = self.parent
        while parent:
            path.insert(0, parent.name)
            parent = parent.parent
        return " > ".join(path)


class ProductImageType(DjangoObjectType):
    """Ảnh chung của sản phẩm (đại diện + gallery)"""
    class Meta:
        model = ProductImage
        fields = '__all__'
        interfaces = (relay.Node,)


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
    """Tùy chọn cụ thể cho thuộc tính (Size 39, Color Đen...)"""
    class Meta:
        model = ProductAttributeOption
        fields = '__all__'
        interfaces = (relay.Node,)
    
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
        """Tính phần trăm giảm giá so với base_price"""
        if self.product.base_price > self.price:
            return float((self.product.base_price - self.price) / self.product.base_price * 100)
        return 0.0
    
    def resolve_original_price(self, info):
        """Giá gốc"""
        return self.product.base_price
    
    def resolve_final_price(self, info):
        """Giá cuối cùng"""
        return self.price
    
    def resolve_color_name(self, info):
        """Lấy tên màu từ option_combinations"""
        return self.color_name
    
    def resolve_size_name(self, info):
        """Lấy size từ option_combinations"""
        return self.size_name
    
    def resolve_color_image_url(self, info):
        """Lấy ảnh màu tương ứng"""
        color_image = self.color_image
        return color_image.image_url if color_image else None
    
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
    
    # ===== THÔNG TIN CƠ BẢN =====
    seller_name = graphene.String(description="Tên người bán")
    seller_avatar = graphene.String(description="Avatar người bán")
    
    # ===== GIÁ CẢ & KHUYẾN MÃI =====
    price_range = graphene.String(description="Khoảng giá")
    min_price = graphene.Decimal(description="Giá thấp nhất")
    max_price = graphene.Decimal(description="Giá cao nhất")
    discount_percentage = graphene.Float(description="% giảm giá cao nhất")
    has_discount = graphene.Boolean(description="Có giảm giá không")
    
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
    rating_count = graphene.Int(description="Số lượng đánh giá")
    
    # ===== TRẠNG THÁI =====
    availability_status = graphene.String(description="Trạng thái hàng")
    
    # ===== THÔNG TIN BỔ SUNG =====
    tags = graphene.List(graphene.String, description="Tags sản phẩm")
    shipping_info = graphene.String(description="Thông tin vận chuyển")
    warranty_info = graphene.String(description="Thông tin bảo hành")
    
    # ===== RESOLVERS =====
    
    def resolve_seller_name(self, info):
        """Tên người bán"""
        return getattr(self.seller, 'username', 'Unknown Seller')
    
    def resolve_seller_avatar(self, info):
        """Avatar người bán"""
        return getattr(self.seller, 'avatar', None)
    
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
        """% giảm giá cao nhất"""
        if self.base_price <= 0:
            return 0.0
        
        variants = self.variants.filter(is_active=True)
        max_discount = 0.0
        
        for variant in variants:
            if self.base_price > variant.price:
                discount = (self.base_price - variant.price) / self.base_price * 100
                max_discount = max(max_discount, discount)
        
        return max_discount
    
    def resolve_has_discount(self, info):
        """Có giảm giá không"""
        return self.resolve_discount_percentage(info) > 0
    
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
        """Tổng số đã bán - TODO: tích hợp với order system"""
        return 0
    
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
        return 4.5  # Mock data
    
    def resolve_rating_count(self, info):
        """Số lượng đánh giá - TODO: tích hợp review system"""
        return 128  # Mock data
    
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
        tags = [self.category.name, self.brand] if self.brand else [self.category.name]
        
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
    brand = graphene.String()
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
                brand=input.get('brand'),
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


# ===== QUERIES =====

class ProductQueries(graphene.ObjectType):
    """Tất cả queries cho sản phẩm"""
    
    # Single queries
    product = graphene.Field(ProductType, id=graphene.ID(required=True))
    product_variant = graphene.Field(ProductVariantType, id=graphene.ID(required=True))
    category = graphene.Field(CategoryType, id=graphene.ID(required=True))
    
    # List queries
    products = graphene.List(
        ProductType,
        category_id=graphene.ID(),
        seller_id=graphene.ID(),
        is_featured=graphene.Boolean(),
        search=graphene.String(),
        first=graphene.Int(),
        skip=graphene.Int()
    )
    
    categories = graphene.List(CategoryType, parent_id=graphene.ID())
    
    # Specific queries
    featured_products = graphene.List(ProductType, limit=graphene.Int(default_value=10))
    products_by_color = graphene.List(ProductType, color_name=graphene.String(required=True))
    
    def resolve_product(self, info, id):
        """Lấy sản phẩm theo ID"""
        try:
            return Product.objects.select_related('category', 'seller').prefetch_related(
                'gallery_images', 'attribute_options', 'variants'
            ).get(product_id=id, is_active=True)
        except Product.DoesNotExist:
            return None
    
    def resolve_product_variant(self, info, id):
        """Lấy variant theo ID"""
        try:
            return ProductVariant.objects.select_related('product').get(
                variant_id=id, is_active=True
            )
        except ProductVariant.DoesNotExist:
            return None
    
    def resolve_category(self, info, id):
        """Lấy danh mục theo ID"""
        try:
            return Category.objects.prefetch_related('subcategories', 'products').get(
                category_id=id, is_active=True
            )
        except Category.DoesNotExist:
            return None
    
    def resolve_products(self, info, **kwargs):
        """Lấy danh sách sản phẩm với filter"""
        queryset = Product.objects.select_related('category', 'seller').prefetch_related(
            'gallery_images', 'variants'
        ).filter(is_active=True)
        
        # Apply filters
        if kwargs.get('category_id'):
            queryset = queryset.filter(category_id=kwargs['category_id'])
        
        if kwargs.get('seller_id'):
            queryset = queryset.filter(seller_id=kwargs['seller_id'])
        
        if kwargs.get('is_featured') is not None:
            queryset = queryset.filter(is_featured=kwargs['is_featured'])
        
        if kwargs.get('search'):
            search = kwargs['search']
            queryset = queryset.filter(
                name__icontains=search
            ) | queryset.filter(
                description__icontains=search
            ) | queryset.filter(
                brand__icontains=search
            )
        
        # Apply pagination
        if kwargs.get('skip'):
            queryset = queryset[kwargs['skip']:]
        
        if kwargs.get('first'):
            queryset = queryset[:kwargs['first']]
            
        return queryset
    
    def resolve_categories(self, info, **kwargs):
        """Lấy danh sách danh mục"""
        queryset = Category.objects.filter(is_active=True)
        
        if kwargs.get('parent_id'):
            queryset = queryset.filter(parent_id=kwargs['parent_id'])
        else:
            queryset = queryset.filter(parent__isnull=True)  # Root categories
            
        return queryset.prefetch_related('subcategories')
    
    def resolve_featured_products(self, info, limit):
        """Lấy sản phẩm nổi bật"""
        return Product.objects.select_related('category').prefetch_related(
            'gallery_images', 'variants'
        ).filter(is_active=True, is_featured=True)[:limit]
    
    def resolve_products_by_color(self, info, color_name):
        """Lấy sản phẩm theo màu sắc"""
        return Product.objects.filter(
            attribute_options__attribute__name='Color',
            attribute_options__value=color_name,
            attribute_options__is_available=True,
            is_active=True
        ).distinct()


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
