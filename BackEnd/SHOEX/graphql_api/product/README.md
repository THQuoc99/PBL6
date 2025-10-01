# Module Product - GraphQL API

Module quản lý sản phẩm GraphQL toàn diện cho nền tảng thương mại điện tử SHOEX theo mẫu kiến trúc Django-Graphene với **Hệ thống Variant và Attribute phức tạp**.

## 📁 Cấu trúc Module

```
graphql_api/product/
├── __init__.py                     # Xuất module
├── schema.py                       # Schema GraphQL chính
├── README.md                       # Tài liệu này
├── types/
│   ├── __init__.py
│   └── product.py                  # Các kiểu GraphQL (ProductType, CategoryType, VariantType)
├── mutations/
│   ├── __init__.py
│   └── product_mutations.py        # Mutations CRUD
├── filters/
│   ├── __init__.py
│   └── product_filters.py          # Lọc và sắp xếp
├── dataloaders/
│   ├── __init__.py
│   └── product_loaders.py          # Tối ưu hóa truy vấn N+1
└── bulk_mutations/
    ├── __init__.py
    ├── bulk_product_mutations.py   # Thao tác hàng loạt sản phẩm
    └── bulk_variants_mutations.py  # Thao tác hàng loạt variants
```

## 🎯 Product Model Integration

Module này tích hợp với hệ thống Product phức tạp của SHOEX (`products/models.py`):

```python
class Category(models.Model):
    """Danh mục sản phẩm - Cây phân cấp"""
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', null=True, blank=True)
    is_active = models.BooleanField(default=True)

class Product(models.Model):
    """Sản phẩm chính - Master data"""
    seller = models.ForeignKey('users.User', related_name='products')
    category = models.ForeignKey(Category, related_name='products')
    name = models.CharField(max_length=200)
    description = models.TextField()
    base_price = models.DecimalField(max_digits=12, decimal_places=2)
    brand = models.CharField(max_length=100)
    model_code = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

class ProductVariant(models.Model):
    """Biến thể sản phẩm - SKU thực tế"""
    product = models.ForeignKey(Product, related_name='variants')
    sku = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    stock = models.IntegerField(default=0)
    weight = models.DecimalField(max_digits=8, decimal_places=2)
    option_combinations = models.JSONField()  # {"Size": "39", "Color": "Đen"}
    is_active = models.BooleanField(default=True)

class ProductAttribute(models.Model):
    """Thuộc tính sản phẩm (Size, Color, Material...)"""
    product = models.ForeignKey(Product, related_name='attributes')
    name = models.CharField(max_length=50)  # "Size", "Color"
    display_name = models.CharField(max_length=100)
    is_required = models.BooleanField(default=True)
    is_variant_attribute = models.BooleanField(default=True)

class ProductAttributeOption(models.Model):
    """Tùy chọn cụ thể cho thuộc tính"""
    attribute = models.ForeignKey(ProductAttribute, related_name='options')
    value = models.CharField(max_length=100)  # "39", "Đen"
    display_value = models.CharField(max_length=100)
    is_available = models.BooleanField(default=True)

class ProductImage(models.Model):
    """Ảnh sản phẩm"""
    product = models.ForeignKey(Product, related_name='gallery_images')
    image_url = models.URLField()
    alt_text = models.CharField(max_length=200)
    is_thumbnail = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)
```

### Các tính năng quan trọng:

- **Hierarchical Categories**: Danh mục cây phân cấp không giới hạn độ sâu
- **Complex Variant System**: Variants với combinations thuộc tính phức tạp
- **Flexible Attributes**: Hệ thống thuộc tính linh hoạt (Size, Color, Material...)
- **Multi-seller Support**: Hỗ trợ nhiều người bán
- **Rich Media**: Quản lý ảnh sản phẩm với thumbnail và gallery
- **Stock Management**: Quản lý tồn kho ở cấp variant
- **Price Flexibility**: Giá cơ bản + giá theo variant

## 🚀 Tính năng

### Kiểu GraphQL

- **ProductType**: Sản phẩm với đầy đủ thông tin và quan hệ
- **ProductVariantType**: Variant với stock, price, attributes
- **CategoryType**: Danh mục với cây phân cấp
- **ProductAttributeType**: Thuộc tính sản phẩm
- **ProductAttributeOptionType**: Tùy chọn thuộc tính
- **ProductImageType**: Ảnh sản phẩm
- **Product/Variant/CategoryConnection**: Hỗ trợ phân trang

### Truy vấn (Queries)

```graphql
# Sản phẩm đơn lẻ
product(id: ID!, slug: String): ProductType
variant(id: ID!, sku: String): ProductVariantType
category(id: ID!, slug: String): CategoryType

# Danh sách với lọc và phân trang
products(
  filter: ProductFilterInput
  sortBy: ProductSortField
  search: String
  first: Int
  after: String
): ProductConnection

variants(
  filter: ProductVariantFilterInput
  sortBy: VariantSortField
): ProductVariantConnection

categories(
  filter: CategoryFilterInput
  level: Int
): CategoryConnection

# Truy vấn chuyên biệt
featuredProducts: ProductConnection
newProducts: ProductConnection
bestSellingProducts: ProductConnection
productsOnSale: ProductConnection
relatedProducts(productId: ID!): ProductConnection
productsInCategory(categoryId: ID!): ProductConnection

# Tìm kiếm
searchProducts(query: String!): ProductConnection
searchSuggestions(query: String!): [String!]

# Attributes và Options
productAttributes(productId: ID!): [ProductAttributeType!]
availableOptions(productId: ID!, attributeName: String!): [ProductAttributeOptionType!]
availableCombinations(productId: ID!): [JSONString!]

# Thống kê
productCount: Int
categoryCount: Int
variantCount: Int
averageProductPrice: Decimal
totalProductValue: Decimal
```

### Thay đổi (Mutations)

```graphql
# Quản lý sản phẩm
productCreate(input: ProductCreateInput!): ProductCreate
productUpdate(id: ID!, input: ProductUpdateInput!): ProductUpdate
productDelete(id: ID!): ProductDelete
productToggleActive(id: ID!): ProductToggleActive
productToggleFeatured(id: ID!): ProductToggleFeatured

# Quản lý variants
variantCreate(input: ProductVariantCreateInput!): ProductVariantCreate
variantUpdate(id: ID!, input: ProductVariantUpdateInput!): ProductVariantUpdate
variantDelete(id: ID!): ProductVariantDelete
stockUpdate(variantId: ID!, stock: Int!): StockUpdate
priceUpdate(variantId: ID!, price: Decimal!): PriceUpdate

# Quản lý danh mục
categoryCreate(input: CategoryCreateInput!): CategoryCreate
categoryUpdate(id: ID!, input: CategoryUpdateInput!): CategoryUpdate
categoryDelete(id: ID!): CategoryDelete
categoryMove(id: ID!, parentId: ID): CategoryMove

# Quản lý attributes
attributeCreate(input: ProductAttributeCreateInput!): ProductAttributeCreate
attributeUpdate(id: ID!, input: ProductAttributeUpdateInput!): ProductAttributeUpdate
attributeDelete(id: ID!): ProductAttributeDelete
attributeOptionCreate(input: AttributeOptionCreateInput!): AttributeOptionCreate

# Thao tác hàng loạt
bulkProductCreate(products: [BulkProductCreateInput!]!): BulkProductCreate
bulkProductUpdate(products: [BulkProductUpdateInput!]!): BulkProductUpdate
bulkVariantCreate(variants: [BulkVariantCreateInput!]!): BulkVariantCreate
bulkStockUpdate(updates: [BulkStockUpdateInput!]!): BulkStockUpdate
bulkPriceUpdate(updates: [BulkPriceUpdateInput!]!): BulkPriceUpdate
bulkProductStatusUpdate(productIds: [ID!]!, isActive: Boolean!): BulkProductStatusUpdate
```

### Lọc & Sắp xếp

```graphql
input ProductFilterInput {
  # Tìm kiếm
  search: String
  name: String
  nameIcontains: String
  description: String
  brand: String
  modelCode: String

  # Lọc theo danh mục
  category: ID
  categoryIn: [ID!]
  categoryTree: ID # Bao gồm danh mục con
  # Lọc theo seller
  seller: ID
  sellerName: String

  # Lọc theo giá
  priceMin: Decimal
  priceMax: Decimal
  basePriceMin: Decimal
  basePriceMax: Decimal

  # Lọc theo trạng thái
  isActive: Boolean
  isFeatured: Boolean
  hasStock: Boolean
  hasVariants: Boolean

  # Lọc theo attributes
  attributes: [AttributeFilterInput!]
  hasAttribute: String

  # Lọc theo thời gian
  createdAfter: DateTime
  createdBefore: DateTime
  updatedAfter: DateTime
  updatedBefore: DateTime
}

input ProductVariantFilterInput {
  product: ID
  sku: String
  skuIcontains: String
  priceMin: Decimal
  priceMax: Decimal
  stockMin: Int
  stockMax: Int
  isActive: Boolean
  hasStock: Boolean
  optionCombinations: JSONString
}

input CategoryFilterInput {
  name: String
  nameIcontains: String
  parent: ID
  level: Int
  isActive: Boolean
  hasProducts: Boolean
}

input AttributeFilterInput {
  name: String!
  value: String!
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

## 🔧 Tích hợp

### 1. Thêm vào Schema GraphQL chính

Trong `graphql_api/schema.py`:

```python
from .product.schema import ProductQuery, ProductMutation

class Query(
    ProductQuery,
    UserQuery,
    CartQuery,
    graphene.ObjectType
):
    pass

class Mutation(
    ProductMutation,
    UserMutation,
    CartMutation,
    graphene.ObjectType
):
    pass
```

### 2. Cấu hình Search Backend

```python
# settings.py
INSTALLED_APPS = [
    # ...
    'django.contrib.postgres',  # Cho full-text search
]

# Sử dụng PostgreSQL full-text search
from django.contrib.postgres.search import SearchVector, SearchQuery
```

### 3. Caching Strategy

```python
# Cache expensive queries
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

# Cache product lists, categories, attributes
```

## 📝 Ví dụ sử dụng

### Ví dụ Truy vấn

```graphql
# Lấy sản phẩm với đầy đủ thông tin
query GetProduct($id: ID!) {
  product(id: $id) {
    id
    name
    description
    brand
    modelCode
    basePrice
    minPrice
    maxPrice
    totalStock
    isActive
    isFeatured
    createdAt

    seller {
      id
      username
      fullName
    }

    category {
      id
      name
      fullPath
    }

    variants {
      edges {
        node {
          id
          sku
          price
          stock
          weight
          isInStock
          isActive
          optionCombinations

          # Computed fields
          discountPercentage
          isOnSale
          availableStock
        }
      }
    }

    attributes {
      id
      name
      displayName
      isRequired
      isVariantAttribute

      options {
        id
        value
        displayValue
        isAvailable
        variantCount
      }
    }

    galleryImages {
      id
      imageUrl
      altText
      isThumbnail
      sortOrder
    }

    # Related data
    relatedProducts {
      edges {
        node {
          id
          name
          minPrice
          thumbnailImage
        }
      }
    }
  }
}

# Tìm kiếm sản phẩm với filters phức tạp
query SearchProducts {
  products(
    filter: {
      search: "giày thể thao"
      categoryTree: "1" # Bao gồm danh mục con
      priceMin: 500000
      priceMax: 2000000
      brand: "Nike"
      hasStock: true
      isActive: true
      attributes: [
        { name: "Size", value: "39" }
        { name: "Color", value: "Đen" }
      ]
    }
    sortBy: PRICE_ASC
    first: 20
  ) {
    edges {
      node {
        id
        name
        brand
        minPrice
        maxPrice
        thumbnailImage
        totalStock

        category {
          name
          fullPath
        }

        # Available attributes cho filtering UI
        availableColors {
          value
          displayValue
          isAvailable
        }

        availableSizes {
          value
          displayValue
          variantCount
        }
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

# Lấy danh mục với cây phân cấp
query GetCategories {
  categories(filter: { level: 0 }) {
    # Root categories
    edges {
      node {
        id
        name
        description
        productCount
        thumbnailImage

        subcategories {
          id
          name
          productCount

          subcategories {
            id
            name
            productCount
          }
        }
      }
    }
  }
}

# Lấy available combinations cho variant selection
query GetAvailableCombinations($productId: ID!) {
  product(id: $productId) {
    id
    name

    attributes {
      name
      displayName

      options {
        value
        displayValue
        isAvailable
        availableCombinations
      }
    }

    availableCombinations
  }
}
```

### Ví dụ Mutations

```graphql
# Tạo sản phẩm mới
mutation CreateProduct {
  productCreate(
    input: {
      name: "Nike Air Max 2024"
      description: "Giày thể thao cao cấp với công nghệ Air Max mới nhất"
      categoryId: 1
      basePrice: "2500000"
      brand: "Nike"
      modelCode: "AIR-MAX-2024"
      isActive: true
      isFeatured: false
    }
  ) {
    success
    product {
      id
      name
      brand
      basePrice
      category {
        name
      }
    }
    errors
  }
}

# Tạo variants cho sản phẩm
mutation CreateVariant {
  variantCreate(
    input: {
      productId: 1
      sku: "NIKE-AIR-MAX-2024-39-BLACK"
      price: "2650000"
      stock: 50
      weight: "0.8"
      optionCombinations: "{\"Size\": \"39\", \"Color\": \"Đen\"}"
      isActive: true
    }
  ) {
    success
    variant {
      id
      sku
      price
      stock
      optionCombinations
    }
    errors
  }
}

# Cập nhật stock hàng loạt
mutation BulkStockUpdate {
  bulkStockUpdate(
    updates: [
      { variantId: "1", stock: 25 }
      { variantId: "2", stock: 30 }
      { variantId: "3", stock: 15 }
    ]
  ) {
    success
    updatedCount
    failedCount
    results {
      variant {
        id
        sku
        stock
      }
      success
      errors
    }
  }
}

# Tạo thuộc tính và options
mutation CreateAttribute {
  attributeCreate(
    input: {
      productId: 1
      name: "Size"
      displayName: "Kích cỡ"
      isRequired: true
      isVariantAttribute: true
    }
  ) {
    success
    attribute {
      id
      name
      displayName

      # Tạo luôn options
      options {
        id
        value
        displayValue
      }
    }
    errors
  }
}

# Tạo danh mục với parent
mutation CreateCategory {
  categoryCreate(
    input: {
      name: "Giày chạy bộ"
      description: "Giày dành cho chạy bộ và thể thao"
      parentId: 1 # Danh mục "Giày thể thao"
      isActive: true
    }
  ) {
    success
    category {
      id
      name
      fullPath
      parent {
        name
      }
    }
    errors
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

- [x] Product types với relationships
- [x] Variant system với attributes
- [x] Category hierarchy
- [x] Search và filtering
- [x] Stock management
- [x] Image handling
- [x] Bulk operations
- [x] DataLoaders optimization
- [x] Permission system
- [x] Error handling

---

**Được tạo cho Nền tảng Thương mại Điện tử SHOEX**
_Hệ thống Product & Variant phức tạp_ ✅
_Theo mẫu kiến trúc Django-Graphene_
