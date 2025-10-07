# Module Product - GraphQL API cho SHOEX

Module quản lý sản phẩm GraphQL toàn diện cho nền tảng thương mại điện tử SHOEX với **Hệ thống Variant, Attribute và Image Upload**.

## 📁 Cấu trúc Module Thực Tế

```
graphql/product/
├── schema.py                       # Schema GraphQL chính - tổng hợp tất cả
├── README.md                       # Tài liệu này
├── types/
│   ├── __init__.py
│   └── product.py                  # Các kiểu GraphQL (ProductType, CategoryType, VariantType, ImageType)
├── mutations/
│   ├── __init__.py
│   ├── product_mutations.py        # Mutations CRUD sản phẩm
│   └── image_mutations.py          # Mutations upload/quản lý ảnh
├── filters/
│   ├── __init__.py
│   └── product_filters.py          # Lọc và sắp xếp sản phẩm
├── dataloaders/
│   ├── __init__.py
│   └── product_loaders.py          # Tối ưu hóa truy vấn N+1
└── bulk_mutations/
    ├── __init__.py
    ├── bulk_product_mutations.py   # Thao tác hàng loạt sản phẩm
    └── bulk_variants_mutations.py  # Thao tác hàng loạt variants
```

## 🎯 Product Model Integration Thực Tế

Module này tích hợp với hệ thống Product của SHOEX (`products/models.py`):

```python
class Category(models.Model):
    """Danh mục sản phẩm - Cây phân cấp"""
    category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='subcategories')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Product(models.Model):
    """Sản phẩm chính - Master data"""
    product_id = models.AutoField(primary_key=True)
    slug = models.SlugField(unique=True, blank=True)  # Auto-generated từ name
    seller = models.ForeignKey('users.User', related_name='products')
    category = models.ForeignKey(Category, related_name='products')
    name = models.CharField(max_length=200)
    description = models.TextField()
    base_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    brand = models.CharField(max_length=100, blank=True, null=True)
    model_code = models.CharField(max_length=100, unique=True)  # Auto: "PRD-0001"
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Properties
    @property
    def min_price(self): # Giá thấp nhất từ variants
    @property
    def max_price(self): # Giá cao nhất từ variants
    @property
    def total_stock(self): # Tổng tồn kho từ variants

class ProductVariant(models.Model):
    """Biến thể sản phẩm - SKU thực tế"""
    variant_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, related_name='variants')
    sku = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    stock = models.IntegerField(default=0)
    weight = models.DecimalField(max_digits=8, decimal_places=2, default=0.1)
    option_combinations = models.JSONField()  # {"Size": "39", "Color": "Đen"}
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Properties
    @property
    def color_name(self): # Lấy màu từ option_combinations
    @property
    def size_name(self): # Lấy size từ option_combinations
    @property
    def is_in_stock(self): # Kiểm tra còn hàng
    @property
    def color_image(self): # Lấy ảnh màu tương ứng

class ProductAttribute(models.Model):
    """Định nghĩa thuộc tính (Size, Color, Material...)"""
    attribute_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)  # "Size", "Color"
    type = models.CharField(max_length=10, choices=[
        ('select', 'Lựa chọn từ danh sách'),
        ('color', 'Màu sắc (có ảnh)'),
        ('text', 'Nhập text'),
        ('number', 'Số'),
    ])
    is_required = models.BooleanField(default=True)
    has_image = models.BooleanField(default=False)  # Có ảnh riêng không
    display_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

class ProductAttributeOption(models.Model):
    """Tùy chọn thuộc tính cho từng sản phẩm"""
    option_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, related_name='attribute_options')
    attribute = models.ForeignKey(ProductAttribute, related_name='product_options')
    value = models.CharField(max_length=100)  # "39", "Đen", "Da thật"
    value_code = models.CharField(max_length=50, blank=True, null=True)  # "#000000", "XL"
    image = models.ImageField(upload_to='products/attributes/%Y/%m/', blank=True, null=True)
    display_order = models.IntegerField(default=0)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Methods
    def get_variants(self): # Lấy variants có tùy chọn này
    def get_available_combinations(self): # Lấy kết hợp có sẵn
    @property
    def image_url(self): # URL ảnh cho backward compatibility

class ProductImage(models.Model):
    """Ảnh sản phẩm với upload thật"""
    image_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, related_name='gallery_images')
    image = models.ImageField(upload_to='products/gallery/%Y/%m/')  # Upload thật!
    is_thumbnail = models.BooleanField(default=False)  # Chỉ 1 ảnh/product
    alt_text = models.CharField(max_length=200, blank=True, null=True)
    display_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def image_url(self): # Trả về self.image.url
```

### Các tính năng đã triển khai:

- **Auto Slug & Model Code**: Tự động tạo slug từ tên và model_code "PRD-0001"
- **Hierarchical Categories**: Danh mục cây phân cấp với subcategories
- **Complex Variant System**: Variants với JSON option_combinations
- **Flexible Attributes**: 4 loại thuộc tính (select, color, text, number)
- **Image Upload System**: Upload ảnh thật với ImageField, auto resize
- **Multi-seller Support**: Mỗi sản phẩm thuộc về 1 seller
- **Rich Media**: Quản lý ảnh với thumbnail unique và gallery
- **Stock Management**: Tồn kho real-time ở cấp variant
- **Price Flexibility**: Base price + variant price với min/max properties

## 🚀 Tính năng

### Kiểu GraphQL

- **ProductType**: Sản phẩm với đầy đủ thông tin và quan hệ
- **ProductVariantType**: Variant với stock, price, attributes
- **CategoryType**: Danh mục với cây phân cấp
- **ProductAttributeType**: Thuộc tính sản phẩm
- **ProductAttributeOptionType**: Tùy chọn thuộc tính
- **ProductImageType**: Ảnh sản phẩm
- **Product/Variant/CategoryConnection**: Hỗ trợ phân trang

### Truy vấn (Queries) Có sẵn

```graphql
	# === QUERIES CƠ BẢN ===
query {
  # Health check
  health

  # Sản phẩm đơn lẻ
  product(id: ID!) {
    productId
    name
    slug
    description
    basePrice
    minPrice  # từ variants
    maxPrice  # từ variants
    totalStock  # từ variants
    brand
    modelCode
    isActive
    isFeatured
    createdAt
    updatedAt

    # Quan hệ
    seller { username }
    category { name, fullPath }
    variants { edges { node { sku, price, stock } } }
    galleryImages { imageUrl, isThumbnail }
    thumbnailImage { imageUrl }
    attributeOptions { value, imageUrl }
  }

  # Variant đơn lẻ
  productVariant(id: ID!) {
    variantId
    sku
    price
    stock
    weight
    optionCombinations  # JSON
    colorName    # từ optionCombinations
    sizeName     # từ optionCombinations
    isInStock    # computed
    colorImageUrl  # từ color option
    isActive

    product { name }
  }

  # Danh mục đơn lẻ
  category(id: ID!) {
    categoryId
    name
    description
    fullPath     # computed path
    productCount # số sản phẩm
    thumbnailImage  # từ featured product
    isActive

    # Cây phân cấp
    parent { name }
    subcategories { name }
  }
}

# === QUERIES DANH SÁCH với Relay Pagination ===
query {
  # Tất cả sản phẩm
  products(first: 10, after: "cursor") {
    edges {
      node {
        productId
        name
        minPrice
        thumbnailImage { imageUrl }
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
    totalCount
  }

  # Sản phẩm với filter
  products(
    filter: {
      search: "giày"
      categoryId: 1
      sellerId: 2
      isActive: true
      isFeatured: true
      priceMin: 100000
      priceMax: 500000
    }
    sortBy: PRICE_ASC
  ) {
    edges { node { name, minPrice } }
  }

  # Variants
  productVariants(first: 20) {
    edges {
      node {
        sku
        price
        stock
        product { name }
      }
    }
  }

  # Categories
  categories {
    edges {
      node {
        name
        productCount
        subcategories { name }
      }
    }
  }
}

# === QUERIES CHUYÊN BIỆT ===
query {
  # Sản phẩm nổi bật
  featuredProducts(first: 10) {
    edges { node { name, minPrice } }
  }

  # Sản phẩm mới
  newProducts(first: 10) {
    edges { node { name, createdAt } }
  }

  # Sản phẩm trong danh mục
  productsInCategory(categoryId: 1, first: 10) {
    edges { node { name } }
  }

  # Sản phẩm của seller
  productsBySeller(sellerId: 1, first: 10) {
    edges { node { name } }
  }
}

# === THỐNG KÊ ===
query {
  productStats {
    totalProducts
    totalVariants
    totalCategories
    averagePrice
    totalValue
    activeProducts
    featuredProducts
  }
}
```

### Thay đổi (Mutations) Có sẵn

```graphql
# === PRODUCT CRUD ===
mutation {
  # Tạo sản phẩm mới
  productCreate(
    input: {
      name: "Giày Nike Air Max 2024"
      description: "Giày thể thao cao cấp"
      categoryId: 1
      basePrice: "2500000"
      brand: "Nike"
      # slug và modelCode tự động tạo
      isActive: true
      isFeatured: false
    }
  ) {
    product {
      productId
      name
      slug # auto: "giay-nike-air-max-2024"
      modelCode # auto: "PRD-0001"
    }
    errors {
      message
    }
  }

  # Update sản phẩm
  productUpdate(
    id: "1"
    input: {
      name: "Giày Nike Air Max 2024 Updated"
      basePrice: "2600000"
      isFeatured: true
    }
  ) {
    product {
      name
      basePrice
      isFeatured
    }
    errors {
      message
    }
  }

  # Xóa sản phẩm
  productDelete(id: "1") {
    success
    errors {
      message
    }
  }
}

# === VARIANT CRUD ===
mutation {
  # Tạo variant
  productVariantCreate(
    input: {
      productId: 1
      sku: "NIKE-AIR-MAX-39-BLACK"
      price: "2650000"
      stock: 50
      weight: "0.8"
      optionCombinations: "{\"Size\": \"39\", \"Color\": \"Black\"}"
      isActive: true
    }
  ) {
    productVariant {
      variantId
      sku
      colorName # "Black" từ JSON
      sizeName # "39" từ JSON
      isInStock # true vì stock > 0
    }
    errors {
      message
    }
  }

  # Update stock
  stockUpdate(variantId: "1", stock: 30) {
    productVariant {
      sku
      stock
      isInStock
    }
    errors {
      message
    }
  }

  # Update price
  priceUpdate(variantId: "1", price: "2700000") {
    productVariant {
      sku
      price
    }
    errors {
      message
    }
  }
}

# === CATEGORY CRUD ===
mutation {
  # Tạo danh mục
  categoryCreate(
    input: {
      name: "Giày thể thao"
      description: "Các loại giày dành cho thể thao"
      parentId: null # Root category
      isActive: true
    }
  ) {
    category {
      categoryId
      name
      fullPath # "Giày thể thao"
    }
    errors {
      message
    }
  }

  # Tạo danh mục con
  categoryCreate(
    input: {
      name: "Giày chạy bộ"
      parentId: 1 # Con của "Giày thể thao"
      isActive: true
    }
  ) {
    category {
      name
      fullPath # "Giày thể thao > Giày chạy bộ"
      parent {
        name
      }
    }
  }
}

# === IMAGE UPLOAD ===
mutation UploadProductImage(
  $productId: ID!
  $image: Upload!
  $isThumbnail: Boolean
) {
  uploadProductImage(
    productId: $productId
    image: $image
    isThumbnail: $isThumbnail
    altText: "Ảnh sản phẩm Nike"
  ) {
    productImage {
      imageId
      imageUrl # http://localhost:8000/media/products/gallery/2025/10/image.jpg
      isThumbnail
      altText
      displayOrder
    }
    errors {
      message
    }
  }
}

mutation UploadAttributeOptionImage($optionId: ID!, $image: Upload!) {
  uploadAttributeOptionImage(optionId: $optionId, image: $image) {
    attributeOption {
      optionId
      value # "Black"
      imageUrl # http://localhost:8000/media/products/attributes/2025/10/black.jpg
    }
    errors {
      message
    }
  }
}

mutation DeleteProductImage($imageId: ID!) {
  deleteProductImage(imageId: $imageId) {
    success # File sẽ tự động xóa
    errors {
      message
    }
  }
}

# === BULK OPERATIONS ===
mutation {
  # Bulk tạo sản phẩm
  bulkProductCreate(
    products: [
      { name: "Sản phẩm 1", categoryId: 1, basePrice: "100000" }
      { name: "Sản phẩm 2", categoryId: 1, basePrice: "200000" }
    ]
  ) {
    products {
      productId
      name
      modelCode
    }
    successCount
    errors {
      message
    }
  }

  # Bulk update stock
  bulkStockUpdate(
    updates: [{ variantId: "1", stock: 25 }, { variantId: "2", stock: 30 }]
  ) {
    results {
      productVariant {
        sku
        stock
      }
      success
    }
    successCount
    failedCount
  }
}
```

### Lọc & Sắp xếp Thực Tế

```graphql
# === PRODUCT FILTERS ===
input ProductFilterInput {
  # Tìm kiếm text
  search: String # Tìm trong name, description
  name: String # Exact match
  nameIcontains: String # Contains (case-insensitive)
  brand: String # Exact brand
  modelCode: String # Exact model code
  # Lọc theo ID
  categoryId: ID # Thuộc danh mục cụ thể
  sellerId: ID # Của seller cụ thể
  # Lọc theo giá (từ min_price, max_price properties)
  priceMin: Decimal # Giá tối thiểu
  priceMax: Decimal # Giá tối đa
  basePriceMin: Decimal # Base price tối thiểu
  basePriceMax: Decimal # Base price tối đa
  # Lọc theo trạng thái
  isActive: Boolean # Sản phẩm active
  isFeatured: Boolean # Sản phẩm nổi bật
  hasStock: Boolean # Có tồn kho (từ variants)
  hasVariants: Boolean # Có variants
  hasImages: Boolean # Có ảnh
  # Lọc theo thời gian
  createdAfter: DateTime # Tạo sau ngày
  createdBefore: DateTime # Tạo trước ngày
}

# === VARIANT FILTERS ===
input ProductVariantFilterInput {
  productId: ID # Thuộc sản phẩm
  sku: String # Exact SKU
  skuIcontains: String # SKU contains
  # Lọc theo giá variant
  priceMin: Decimal
  priceMax: Decimal

  # Lọc theo stock
  stockMin: Int
  stockMax: Int
  hasStock: Boolean # stock > 0
  # Lọc theo trạng thái
  isActive: Boolean

  # Lọc theo attributes trong JSON
  colorName: String # Màu trong optionCombinations
  sizeName: String # Size trong optionCombinations
}

# === CATEGORY FILTERS ===
input CategoryFilterInput {
  name: String
  nameIcontains: String
  parentId: ID # Thuộc parent category
  level: Int # Cấp độ trong cây (0=root)
  isActive: Boolean
  hasProducts: Boolean # Có sản phẩm
}

# === SORTING ===
enum ProductSortingField {
  NAME # Theo tên A-Z
  NAME_DESC # Theo tên Z-A
  PRICE # Theo giá thấp → cao
  PRICE_DESC # Theo giá cao → thấp
  CREATED_AT # Cũ → mới
  CREATED_AT_DESC # Mới → cũ (default)
  UPDATED_AT # Ít update → nhiều update
  UPDATED_AT_DESC # Nhiều update → ít update
  STOCK # Ít hàng → nhiều hàng
  STOCK_DESC # Nhiều hàng → ít hàng
}

enum ProductVariantSortingField {
  SKU
  SKU_DESC
  PRICE
  PRICE_DESC
  STOCK
  STOCK_DESC
  CREATED_AT
  CREATED_AT_DESC
}

# === VÍ DỤ SỬ DỤNG FILTERS ===
query {
  # Tìm giày Nike có giá 1-3 triệu, còn hàng, active
  products(
    filter: {
      search: "giày"
      brand: "Nike"
      priceMin: 1000000
      priceMax: 3000000
      hasStock: true
      isActive: true
    }
    sortBy: PRICE
    first: 20
  ) {
    edges {
      node {
        name
        brand
        minPrice
        totalStock
      }
    }
  }

  # Variants size 39, màu đen, còn hàng
  productVariants(
    filter: {
      sizeName: "39"
      colorName: "Black"
      hasStock: true
      isActive: true
    }
    sortBy: PRICE
  ) {
    edges {
      node {
        sku
        price
        stock
        colorName
        sizeName
      }
    }
  }
}
```

### DataLoaders (Tối ưu hóa N+1)

- `ProductLoader`: Tải sản phẩm theo batch theo ID
- `ProductBySlugLoader`: Tải sản phẩm theo slug
- `ProductVariantLoader`: Tải variants theo batch
- `ProductVariantsByProductLoader`: Tải variants theo product
- `CategoryLoader`: Tải danh mục theo batch
- `CategoryChildrenLoader`: Tải danh mục con
- `ProductAttributeLoader`: Tải attributes theo product
- `ProductImageLoader`: Tải ảnh theo product
- `ProductStatsLoader`: Tải thống kê sản phẩm
- `VariantStockLoader`: Tải tồn kho variants
- `RelatedProductsLoader`: Tải sản phẩm liên quan

## 🔧 Tích hợp Thực Tế

### 1. Schema GraphQL chính đã tích hợp

Trong `graphql/api.py`:

```python
import graphene

# Import từ product app
from .product.schema import ProductQueries, ProductMutations

# Import từ user app
from .user.schema import UserQuery, UserMutation

class Query(
    ProductQueries,      # ✅ Đã tích hợp
    UserQuery,
    graphene.ObjectType
):
    # Root field cho health check
    health = graphene.String(description="Health check endpoint")

    def resolve_health(self, info):
        return "SHOEX GraphQL API is running!"

class Mutation(
    ProductMutations,    # ✅ Đã tích hợp (bao gồm image upload)
    UserMutation,
    graphene.ObjectType
):
    pass

# Schema đã export
schema = graphene.Schema(query=Query, mutation=Mutation)
```

### 2. Settings đã cấu hình

```python
# config/settings.py - ✅ ĐÃ SETUP
INSTALLED_APPS = [
    'graphene_django',
    'graphene_file_upload',    # Cho image upload
    'products',
    # ...
]

GRAPHENE = {
    "SCHEMA": "graphql.api.schema",  # ✅ Đã trỏ đúng
    'MIDDLEWARE': [
        'graphene_file_upload.django.FileUploadGraphQLMiddleware',
    ],
}

# Media files cho image upload - ✅ ĐÃ SETUP
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

### 3. URLs đã cấu hình

```python
# config/urls.py - ✅ ĐÃ SETUP
from graphene_django.views import GraphQLView
from graphql.api import schema

urlpatterns = [
    path('admin/', admin.site.urls),
    path('graphql/', GraphQLView.as_view(graphiql=True, schema=schema)),
]

# Serve media files in development - ✅ ĐÃ SETUP
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### 4. Database đã migrate

```bash
# ✅ ĐÃ CHẠY
python manage.py makemigrations products
python manage.py migrate products

# Kết quả: Products models với ImageField đã sẵn sàng
```

### 5. Server sẵn sàng

```bash
# ✅ ĐANG CHẠY
python manage.py runserver
# GraphQL Playground: http://127.0.0.1:8000/graphql/
```

## 📝 Ví dụ sử dụng Thực Tế

### Test trên GraphQL Playground: http://127.0.0.1:8000/graphql/

#### Ví dụ Query Hoàn Chỉnh

```graphql
# === 1. HEALTH CHECK ===
query HealthCheck {
  health # "SHOEX GraphQL API is running!"
}

# === 2. LẤY SẢN PHẨM ĐẦY ĐỦ ===
query GetProductComplete($id: ID!) {
  product(id: $id) {
    # Thông tin cơ bản
    productId
    name
    slug # auto-generated
    description
    brand
    modelCode # auto: "PRD-0001"
    # Giá cả
    basePrice
    minPrice # computed từ variants
    maxPrice # computed từ variants
    priceRange # formatted: "1,000,000đ - 2,000,000đ"
    # Trạng thái & thống kê
    isActive
    isFeatured
    totalStock # computed từ variants
    variantCount # số lượng variants
    availabilityStatus # "in_stock", "low_stock", "out_of_stock"
    # Thời gian
    createdAt
    updatedAt

    # === QUAN HỆ ===
    seller {
      username
      fullName
    }

    category {
      categoryId
      name
      fullPath # "Thời trang > Giày dép > Giày thể thao"
      parent {
        name
      }
    }

    # === IMAGES (Đã upload thật) ===
    galleryImages {
      imageId
      imageUrl # http://localhost:8000/media/products/gallery/2025/10/image.jpg
      isThumbnail
      altText
      displayOrder
      createdAt
    }

    thumbnailImage {
      imageUrl # Ảnh đại diện
      altText
    }

    # === VARIANTS ===
    variants {
      edges {
        node {
          variantId
          sku
          price
          stock
          weight

          # JSON parsed properties
          colorName # từ optionCombinations JSON
          sizeName # từ optionCombinations JSON
          # Computed properties
          isInStock # stock > 0 && is_active
          stockStatus # "in_stock", "low_stock", "out_of_stock"
          discountPercentage # so với basePrice
          # Ảnh màu (nếu có)
          colorImageUrl # từ attribute option image
          isActive
          createdAt
        }
      }
    }

    # === ATTRIBUTE OPTIONS ===
    attributeOptions {
      optionId
      value # "39", "Black", "Da thật"
      valueCode # "#000000", "XL"
      imageUrl # http://localhost:8000/media/products/attributes/2025/10/black.jpg
      displayOrder
      isAvailable

      attribute {
        name # "Size", "Color", "Material"
        type # "select", "color", "text", "number"
        hasImage # true/false
      }

      variantCount # Số variants có option này
      availableCombinations # JSON: các kết hợp còn lại
    }

    # Grouped by attribute
    colorOptions {
      value # "Black", "White", "Red"
      imageUrl
      variantCount
    }

    sizeOptions {
      value # "39", "40", "41"
      variantCount
    }
  }
}

# Variables:
# { "id": "1" }

# === 3. TÌM KIẾM SẢN PHẨM PHỨC TẠP ===
query SearchProductsAdvanced {
  products(
    filter: {
      search: "giày Nike"
      brand: "Nike"
      categoryId: 1
      priceMin: 1000000
      priceMax: 3000000
      hasStock: true
      isActive: true
      isFeatured: null # null = không filter
    }
    sortBy: NAME # NAME, PRICE, CREATED_AT_DESC, etc.
    first: 10
    after: null
  ) {
    edges {
      node {
        productId
        name
        slug
        brand
        minPrice
        maxPrice
        totalStock
        thumbnailImage {
          imageUrl
        }

        category {
          name
          fullPath
        }

        # Quick stats
        variantCount
        availabilityStatus
      }
    }

    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
    }

    totalCount
  }
}

# === 4. CATEGORY TREE ===
query GetCategoryTree {
  categories {
    edges {
      node {
        categoryId
        name
        description
        productCount # số sản phẩm active
        thumbnailImage # từ featured product đầu tiên
        fullPath

        # Cây phân cấp
        parent {
          name
        }
        subcategories {
          categoryId
          name
          productCount

          subcategories {
            categoryId
            name
            productCount
          }
        }

        isActive
        createdAt
      }
    }
  }
}

# === 5. VARIANTS CỦA PRODUCT ===
query GetProductVariants($productId: ID!) {
  productVariants(
    filter: { productId: $productId, isActive: true }
    sortBy: PRICE
  ) {
    edges {
      node {
        variantId
        sku
        price
        stock

        colorName
        sizeName
        colorImageUrl

        isInStock
        stockStatus

        product {
          name
          brand
        }
      }
    }
  }
}

# Variables:
# { "productId": "1" }

# === 6. FEATURED & NEW PRODUCTS ===
query GetSpecialProducts {
  # Sản phẩm nổi bật
  featuredProducts(first: 5) {
    edges {
      node {
        name
        minPrice
        thumbnailImage {
          imageUrl
        }
        brand
      }
    }
  }

  # Sản phẩm mới
  newProducts(first: 5) {
    edges {
      node {
        name
        createdAt
        minPrice
        thumbnailImage {
          imageUrl
        }
      }
    }
  }

  # Thống kê
  productStats {
    totalProducts
    totalVariants
    totalCategories
    averagePrice
    activeProducts
    featuredProducts
  }
}
```

#### Ví dụ Mutation Hoàn Chỉnh

```graphql
# === 1. TẠO SẢN PHẨM MỚI ===
mutation CreateProduct {
  productCreate(input: {
    name: "Nike Air Max 2024"
    description: "Giày thể thao cao cấp với công nghệ Air Max mới nhất từ Nike"
    categoryId: 1
    basePrice: "2500000"
    brand: "Nike"
    # slug và modelCode sẽ tự động tạo
    isActive: true
    isFeatured: false
  }) {
    product {
      productId
      name
      slug                 # auto: "nike-air-max-2024"
      modelCode            # auto: "PRD-0001", "PRD-0002", ...
      basePrice
      brand

      category {
        name
        fullPath
      }
    }
    errors {
      message
      field
    }
  }
}

# === 2. TẠO VARIANTS CHO SẢN PHẨM ===
mutation CreateVariants {
  # Variant 1: Size 39, Black
  productVariantCreate(input: {
    productId: 1
    sku: "NIKE-AIR-MAX-2024-39-BLACK"
    price: "2650000"
    stock: 50
    weight: "0.8"
    optionCombinations: "{\"Size\": \"39\", \"Color\": \"Black\"}"
    isActive: true
  }) {
    productVariant {
      variantId
      sku
      price
      stock
      colorName          # "Black" - parsed từ JSON
      sizeName           # "39" - parsed từ JSON
      isInStock          # true
      stockStatus        # "in_stock"
    }
    errors { message }
  }
}

# Tạo thêm variant khác
mutation CreateVariant2 {
  productVariantCreate(input: {
    productId: 1
    sku: "NIKE-AIR-MAX-2024-40-WHITE"
    price: "2650000"
    stock: 30
    weight: "0.8"
    optionCombinations: "{\"Size\": \"40\", \"Color\": \"White\"}"
    isActive: true
  }) {
    productVariant {
      sku
      colorName          # "White"
      sizeName           # "40"
    }
  }
}

# === 3. UPLOAD ẢNH SẢN PHẨM ===
# Chú ý: Cần dùng multipart form data
mutation UploadProductImage($productId: ID!, $image: Upload!, $isThumbnail: Boolean) {
  uploadProductImage(
    productId: $productId
    image: $image
    isThumbnail: $isThumbnail
    altText: "Ảnh Nike Air Max 2024"
    displayOrder: 0
  ) {
    productImage {
      imageId
      imageUrl             # http://localhost:8000/media/products/gallery/2025/10/nike_air_max.jpg
      isThumbnail
      altText
      displayOrder
      createdAt
    }
    errors { message }
  }
}

# Variables cho upload:
# {
#   "productId": "1",
#   "isThumbnail": true
# }
# File: Chọn file ảnh trong GraphQL Playground

# === 4. TẠO ATTRIBUTE OPTIONS VỚI ẢNH ===
# Trước tiên tạo attribute option cho màu sắc
mutation CreateColorOption {
  # Note: Mutation này có thể cần tạo riêng trong mutations
  # Hoặc có thể tạo qua Django Admin trước
}

# Upload ảnh cho color option
mutation UploadColorImage($optionId: ID!, $image: Upload!) {
  uploadAttributeOptionImage(optionId: $optionId, image: $image) {
    attributeOption {
      optionId
      value              # "Black"
      valueCode          # "#000000"
      imageUrl           # http://localhost:8000/media/products/attributes/2025/10/black_color.jpg

      attribute {
        name             # "Color"
        type             # "color"
        hasImage         # true
      }
    }
    errors { message }
  }
}

# === 5. CẬP NHẬT STOCK & PRICE ===
mutation UpdateStock {
  stockUpdate(variantId: "1", stock: 25) {
    productVariant {
      sku
      stock
      isInStock          # Có thể thay đổi từ true → false
      stockStatus        # "low_stock" nếu <= 5
    }
    errors { message }
  }
}

mutation UpdatePrice {
  priceUpdate(variantId: "1", price: "2800000") {
    productVariant {
      sku
      price
      discountPercentage # So với basePrice
    }
    errors { message }
  }
}

# === 6. TẠO DANH MỤC ===
mutation CreateCategory {
  categoryCreate(input: {
    name: "Giày chạy bộ"
    description: "Giày dành riêng cho chạy bộ và marathon"
    parentId: 1          # Con của danh mục "Giày thể thao"
    isActive: true
  }) {
    category {
      categoryId
      name
      description
      fullPath           # "Giày thể thao > Giày chạy bộ"

      parent {
        name
        categoryId
      }

      productCount       # 0 ban đầu
      thumbnailImage     # null ban đầu
    }
    errors { message }
  }
}

# === 7. CẬP NHẬT SẢN PHẨM ===
mutation UpdateProduct {
  productUpdate(id: "1", input: {
    name: "Nike Air Max 2024 Premium Edition"
    basePrice: "2700000"
    isFeatured: true
    description: "Phiên bản cao cấp với chất liệu da thật"
  }) {
    product {
      productId
      name
      basePrice
      isFeatured
      description
      updatedAt
    }
    errors { message }
  }
}

# === 8. XÓA ẢNH ===
mutation DeleteImage {
  deleteProductImage(imageId: "img_123") {
    success              # File sẽ tự động xóa khỏi storage
    errors { message }
  }
}

# === 9. BULK OPERATIONS ===
mutation BulkUpdateStock {
  bulkStockUpdate(updates: [
    { variantId: "1", stock: 20 },
    { variantId: "2", stock: 35 },
    { variantId: "3", stock: 0 }     # Out of stock
  ]) {
    results {
      productVariant {
        sku
        stock
        stockStatus
        isInStock
      }
      success
      errors { message }
    }
    successCount         # Số lượng update thành công
    failedCount          # Số lượng failed
  }
}

mutation BulkCreateProducts {
  bulkProductCreate(products: [
    {
      name: "Adidas Ultraboost 2024"
      categoryId: 1
      basePrice: "3200000"
      brand: "Adidas"
    },
    {
      name: "Puma RS-X Future"
      categoryId: 1
      basePrice: "2800000"
      brand: "Puma"
    }
  ]) {
    products {
      productId
      name
      slug
      modelCode          # Tự động: PRD-0002, PRD-0003
      brand
    }
    successCount
    errors { message }
  }
}
```

## 🔒 Xác thực & Quyền

- **Public Access**: Queries công khai cho catalog browsing
- **Seller Access**: Seller chỉ có thể quản lý sản phẩm của mình
- **Admin Access**: Admin có thể quản lý tất cả sản phẩm
- **Category Management**: Chỉ admin có thể quản lý danh mục
- **Stock Updates**: Seller và admin có thể cập nhật stock
- **Bulk Operations**: Yêu cầu quyền đặc biệt cho thao tác hàng loạt

## 🎯 Thực hành tốt nhất

1. **Variant Strategy**: Luôn tạo variants cho các sản phẩm có tùy chọn
2. **Attribute Planning**: Thiết kế attributes trước khi tạo products
3. **Image Optimization**: Tối ưu hóa ảnh và sử dụng CDN
4. **Search Optimization**: Sử dụng full-text search cho performance
5. **Stock Management**: Cập nhật stock real-time
6. **Category Structure**: Thiết kế cây danh mục hợp lý, không quá sâu

## 🔗 Các Module liên quan

- **User Module**: Seller management và product ownership
- **Cart Module**: Product variants trong giỏ hàng
- **Order Module**: Product fulfillment và inventory
- **Review Module**: Product ratings và reviews
- **Discount Module**: Product discounts và promotions

## 📊 Cân nhắc về hiệu suất

- **Database Indexing**: Index trên category, seller, price, stock
- **Query Optimization**: Sử dụng select_related và prefetch_related
- **Caching Strategy**: Cache product lists, categories, attributes
- **Search Performance**: PostgreSQL full-text search hoặc Elasticsearch
- **Image Optimization**: CDN và lazy loading
- **Variant Loading**: Batch load variants để tránh N+1

## 🧪 Kiểm thử & Xác thực

### Testing Steps

1. **Setup Test Data**:

   ```python
   # Tạo categories
   electronics = Category.objects.create(name="Electronics")
   phones = Category.objects.create(name="Phones", parent=electronics)

   # Tạo products với variants
   iphone = Product.objects.create(
       name="iPhone 15",
       category=phones,
       seller=seller_user
   )
   ```
2. **Test Complex Queries**:

   ```graphql
   # Test search với multiple filters
   # Test category tree queries
   # Test variant combinations
   ```
3. **Test Mutations**:

   ```python
   # Test product CRUD
   # Test variant management
   # Test bulk operations
   ```

### Kết quả mong đợi

- ✅ Products với variants load chính xác
- ✅ Category tree navigation hoạt động
- ✅ Search với filters phức tạp
- ✅ Attribute combinations đúng
- ✅ Stock management real-time
- ✅ Bulk operations hiệu quả
- ✅ Performance tốt với dataset lớn

### Danh sách kiểm tra tích hợp

- [X] Product types với relationships
- [X] Variant system với attributes
- [X] Category hierarchy
- [X] Search và filtering
- [X] Stock management
- [X] Image handling
- [X] Bulk operations
- [X] DataLoaders optimization
- [X] Permission system
- [X] Error handling

## 🔍 Advanced Filtering & Search

### Lọc và Sắp xếp Nâng cao

```graphql
# === FILTER SẢN PHẨM ===
query AdvancedProductFilter {
  # Lọc theo khoảng giá với variants
  products(
    filters: {
      priceRange: { min: 1000000, max: 3000000 }
      hasStock: true # Chỉ lấy sản phẩm còn hàng
      isActive: true
    }
  ) {
    edges {
      node {
        productId
        name
        brand

        # Giá min-max từ variants
        minPrice # Giá thấp nhất của variants
        maxPrice # Giá cao nhất của variants
        # Stock info
        totalStock # Tổng stock từ tất cả variants
        inStockVariants # Số variants còn hàng
        variants {
          price
          stock
          isInStock
          stockStatus
        }
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}

# === FILTER THEO NHIỀU TIÊU CHÍ ===
query ComplexFilter {
  products(
    filters: {
      # Brand filters
      brand_In: ["Nike", "Adidas", "Puma"] # Multi-brand
      # Category hierarchy
      categoryId: 1
      includeSubcategories: true # Bao gồm danh mục con
      # Attribute filters
      attributes: [
        { name: "Color", values: ["Black", "White"] }
        { name: "Size", values: ["39", "40", "41"] }
      ]
      # Price range
      priceRange: { min: 2000000, max: 5000000 }
      # Stock filters
      stockRange: { min: 1, max: 100 } # Có từ 1-100 sản phẩm
      hasStock: true
      # Status filters
      isActive: true
      isFeatured: false # Không lấy featured
      # Date filters
      createdAfter: "2024-01-01"
      updatedAfter: "2024-10-01"
      # Search text
      search: "Air Max" # Tìm trong name, description
    }

    # Sắp xếp multiple criteria
    orderBy: [
      FEATURED_DESC # Featured trước
      PRICE_ASC # Giá tăng dần
      CREATED_DESC # Mới nhất
    ]

    # Pagination
    first: 20
    after: "cursor_value"
  ) {
    edges {
      node {
        productId
        name
        slug
        brand

        # Computed fields
        averageRating # 4.5
        reviewCount # 128
        totalSold # 456
        # Price analysis
        minPrice
        maxPrice
        priceRange # "2,500,000 - 3,200,000 VNĐ"
        # Stock analysis
        totalStock
        stockStatus # "in_stock", "low_stock", "out_of_stock"
        # SEO fields
        metaTitle
        metaDescription

        # Relationships
        category {
          name
          fullPath
        }

        thumbnailImage {
          imageUrl
          altText
        }

        # Variants matching filter
        matchingVariants: variants(
          filters: {
            colors: ["Black", "White"]
            sizes: ["39", "40", "41"]
            inStock: true
          }
        ) {
          variantId
          sku
          price
          colorName
          sizeName
          stock
        }
      }
    }

    # Metadata
    totalCount # Tổng số kết quả
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
    }

    # Facets để tạo filter UI
    facets {
      brands {
        value # "Nike"
        count # 45 (số sản phẩm)
      }
      categories {
        categoryId
        name
        count
      }
      priceRanges {
        range # "1-2 triệu"
        min
        max
        count
      }
      colors {
        value
        count
        hexCode # "#000000"
      }
      sizes {
        value
        count
      }
    }
  }
}
```

### Search & Subscription Features

```graphql
# === SMART SEARCH ===
query SmartSearch($query: String!) {
  searchProducts(
    query: $query # "nike air max black 39"
    filters: { isActive: true, hasStock: true }

    # Search configuration
    searchOptions: {
      includeDescription: true # Tìm trong mô tả
      includeBrand: true # Tìm theo brand
      includeAttributes: true # Tìm trong attributes
      fuzzyMatch: true # Cho phép lỗi chính tả
      boost: {
        nameWeight: 2.0 # Tên quan trọng gấp 2x
        brandWeight: 1.5 # Brand quan trọng 1.5x
        descriptionWeight: 1.0 # Description trọng số bình thường
      }
    }

    first: 20
  ) {
    edges {
      node {
        productId
        name
        brand

        # Search scoring
        searchScore # 0.95 (độ khớp với query)
        matchedFields # ["name", "brand"]
        # Highlighted text
        highlightedName # "Nike <em>Air Max</em> 2024"
        highlightedDescription

        variants {
          colorName
          sizeName
          isInStock
        }
      }
    }

    # Search suggestions
    suggestions {
      query # "Did you mean: nike air max?"
      type # "spelling", "completion"
      score
    }

    # Related searches
    relatedQueries # ["nike air force", "adidas ultraboost"]
  }
}

# === REAL-TIME SUBSCRIPTIONS ===
subscription ProductUpdates {
  # Theo dõi thay đổi stock
  stockUpdates {
    variant {
      variantId
      sku
      stock
      stockStatus
      isInStock
    }
    changeType # "STOCK_LOW", "OUT_OF_STOCK", "BACK_IN_STOCK"
    timestamp
  }
}

subscription PriceUpdates {
  # Theo dõi thay đổi giá
  priceUpdates(productIds: ["1", "2", "3"]) {
    product {
      productId
      name
    }
    oldPrice
    newPrice
    changePercentage # +15% or -20%
    timestamp
  }
}

subscription NewProducts {
  # Theo dõi sản phẩm mới trong category
  newProducts(categoryId: 1) {
    product {
      productId
      name
      brand
      thumbnailImage {
        imageUrl
      }
    }
    timestamp
  }
}
```

## ⚙️ Performance & Security

### Optimization Techniques

- **DataLoader**: Batch loading để tránh N+1 queries
- **Fragment Caching**: Cache fragment queries phổ biến
- **Database Indexing**: Index trên `slug`, `brand`, `sku`, `category_id`
- **Image Optimization**: Tự động resize và WebP conversion
- **Query Complexity**: Giới hạn depth và field selections

### Security Measures

- **Authentication**: JWT-based với refresh tokens
- **Authorization**: Permission-based field access
- **Rate Limiting**: GraphQL query complexity scoring
- **Input Validation**: Sanitize uploads và text inputs
- **CORS Configuration**: Strict origin policies

### Monitoring & Analytics

```graphql
query SystemMetrics {
  # Admin-only analytics
  productAnalytics {
    totalProducts
    totalVariants
    totalCategories
    averageStock

    # Performance metrics
    slowQueries {
      query
      avgExecutionTime
      callCount
    }

    # Business metrics
    topSellingProducts(limit: 10) {
      product {
        name
      }
      soldCount
      revenue
    }

    stockAlerts {
      product {
        name
      }
      variant {
        sku
      }
      currentStock
      alertLevel
    }
  }
}
```

---

**Được tạo cho Nền tảng Thương mại Điện tử SHOEX**
_Hệ thống Product & Variant phức tạp_ ✅
_Theo mẫu kiến trúc Django-Graphene_
