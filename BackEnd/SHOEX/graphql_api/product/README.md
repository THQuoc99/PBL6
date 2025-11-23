# 📚 Module Product - GraphQL API Documentation cho SHOEX

Tài liệu chi tiết về **GraphQL API sản phẩm** cho nền tảng thương mại điện tử SHOEX với hệ thống **Variant phức tạp, Attribute linh hoạt và Image Upload thực tế**.

---

## 📋 **MỤC LỤC**

1. [📁 Cấu trúc Module](#-cấu-trúc-module)
2. [🎯 Model Integration](#-model-integration)
3. [🏷️ CATEGORY - Danh mục sản phẩm](#️-category---danh-mục-sản-phẩm)
4. [🛍️ PRODUCT - Sản phẩm chính](#️-product---sản-phẩm-chính)
5. [🎨 PRODUCT VARIANT - Biến thể](#-product-variant---biến-thể)
6. [🖼️ IMAGE SYSTEM - Hệ thống ảnh](#️-image-system---hệ-thống-ảnh)
7. [🔍 ADVANCED FEATURES - Tính năng nâng cao](#-advanced-features---tính-năng-nâng-cao)
8. [🔧 Setup &amp; Integration](#-setup--integration)
9. [📊 Performance &amp; Security](#-performance--security)

---

## 📁 **CẤU TRÚC MODULE**

```
graphql/product/
├── schema.py                       # 🎯 Schema GraphQL chính - ProductQueries & ProductMutations
├── README.md                       # 📚 Tài liệu này (bạn đang đọc)
├── types/
│   ├── __init__.py
│   └── product.py                  # 🏗️ GraphQL Types: ProductType, CategoryType, VariantType, ImageType
├── mutations/
│   ├── __init__.py
│   ├── product_mutations.py        # ✏️ CRUD Operations: Create, Update, Delete
│   └── image_mutations.py          # 📤 Image Upload: Upload, Delete ảnh
├── filters/
│   ├── __init__.py
│   └── product_filters.py          # 🔍 Filtering: ProductFilterInput, CategoryFilterInput
├── dataloaders/
│   ├── __init__.py
│   └── product_loaders.py          # ⚡ Performance: Batch loading, N+1 optimization
└── bulk_mutations/
    ├── __init__.py
    ├── bulk_product_mutations.py   # 📦 Bulk Operations: Mass create, update, delete
    └── bulk_variants_mutations.py  # 🔄 Variant Bulk: Mass variant operations
```

**📌 Vai trò từng file:**

- **`schema.py`**: Entry point chính, chứa ProductQueries và ProductMutations
- **`types/product.py`**: Định nghĩa GraphQL types và Connection classes
- **`mutations/`**: Tất cả operations thay đổi dữ liệu
- **`filters/`**: Logic filtering và sorting cho queries
- **`dataloaders/`**: Tối ưu performance với batch loading
- **`bulk_mutations/`**: Operations hàng loạt cho admin/seller

---

## 🎯 **MODEL INTEGRATION**

### **🏗️ Django Models Architecture**

Module GraphQL này tích hợp với hệ thống Django models trong `products/models.py`:

```python
# ===== CATEGORY MODEL =====
class Category(models.Model):
    """Danh mục sản phẩm - Hệ thống cây phân cấp"""
    category_id = models.AutoField(primary_key=True)     # PK: 1, 2, 3...
    name = models.CharField(max_length=100)              # "Giày thể thao"
    description = models.TextField(blank=True, null=True) # Mô tả chi tiết
    parent = models.ForeignKey('self', null=True, blank=True, related_name='subcategories')  # Cây phân cấp
    is_active = models.BooleanField(default=True)        # Trạng thái hoạt động
    created_at = models.DateTimeField(auto_now_add=True) # Thời gian tạo

# ===== PRODUCT MODEL =====
class Product(models.Model):
    """Sản phẩm chính - Master data với variants"""
    product_id = models.AutoField(primary_key=True)      # PK: 1, 2, 3...
    slug = models.SlugField(unique=True, blank=True)     # Auto: "nike-air-max-2024"
    seller = models.ForeignKey('users.User', related_name='products')  # Người bán
    category = models.ForeignKey(Category, related_name='products')     # Danh mục
    name = models.CharField(max_length=200)              # "Nike Air Max 2024"
    description = models.TextField()                     # Mô tả chi tiết HTML
    base_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)  # Giá gốc
    brand = models.CharField(max_length=100, blank=True, null=True)     # "Nike"
    model_code = models.CharField(max_length=100, unique=True)          # Auto: "PRD-0001"
    is_active = models.BooleanField(default=True)        # Hoạt động
    is_featured = models.BooleanField(default=False)     # Nổi bật
    created_at = models.DateTimeField(auto_now_add=True) # Ngày tạo
    updated_at = models.DateTimeField(auto_now=True)     # Ngày cập nhật

    # 🧮 Computed Properties (từ variants)
    @property
    def min_price(self):    # Giá thấp nhất từ active variants
    @property
    def max_price(self):    # Giá cao nhất từ active variants
    @property
    def total_stock(self):  # Tổng tồn kho từ tất cả variants

# ===== PRODUCT VARIANT MODEL =====
class ProductVariant(models.Model):
    """Biến thể sản phẩm - SKU cụ thể với thuộc tính"""
    variant_id = models.AutoField(primary_key=True)      # PK: 1, 2, 3...
    product = models.ForeignKey(Product, related_name='variants')  # Sản phẩm cha
    sku = models.CharField(max_length=100, unique=True)  # "NIKE-AIR-MAX-39-BLACK"
    price = models.DecimalField(max_digits=12, decimal_places=2)   # Giá cụ thể
    stock = models.IntegerField(default=0)               # Tồn kho
    weight = models.DecimalField(max_digits=8, decimal_places=2, default=0.1)  # Trọng lượng
    option_combinations = models.JSONField()             # {"Size": "39", "Color": "Black"}
    is_active = models.BooleanField(default=True)        # Hoạt động
    created_at = models.DateTimeField(auto_now_add=True) # Ngày tạo
    updated_at = models.DateTimeField(auto_now=True)     # Ngày cập nhật

    # 🎨 JSON Parsed Properties
    @property
    def color_name(self):   # "Black" - parse từ option_combinations["Color"]
    @property
    def size_name(self):    # "39" - parse từ option_combinations["Size"]
    @property
    def is_in_stock(self):  # stock > 0 && is_active == True
    @property
    def color_image(self):  # Lấy ảnh màu từ ProductAttributeOption

# ===== ATTRIBUTE SYSTEM =====
class ProductAttribute(models.Model):
    """Định nghĩa thuộc tính sản phẩm (Size, Color, Material...)"""
    attribute_id = models.AutoField(primary_key=True)    # PK: 1, 2, 3...
    name = models.CharField(max_length=50, unique=True)  # "Size", "Color", "Material"
    type = models.CharField(max_length=10, choices=[     # Loại thuộc tính:
        ('select', 'Lựa chọn từ dropdown'),          #   - Dropdown list
        ('color', 'Màu sắc với ảnh'),             #   - Color picker + image
        ('text', 'Nhập text tự do'),               #   - Free text input
        ('number', 'Nhập số'),                     #   - Number input
    ])
    is_required = models.BooleanField(default=True)      # Bắt buộc hay không
    has_image = models.BooleanField(default=False)       # Có hỗ trợ ảnh không
    display_order = models.IntegerField(default=0)       # Thứ tự hiển thị
    created_at = models.DateTimeField(auto_now_add=True)

class ProductAttributeOption(models.Model):
    """Tùy chọn cụ thể của thuộc tính cho mỗi sản phẩm"""
    option_id = models.AutoField(primary_key=True)       # PK: 1, 2, 3...
    product = models.ForeignKey(Product, related_name='attribute_options')      # Sản phẩm
    attribute = models.ForeignKey(ProductAttribute, related_name='product_options')  # Thuộc tính
    value = models.CharField(max_length=100)             # "39", "Black", "Leather"
    value_code = models.CharField(max_length=50, blank=True, null=True)  # "#000000", "XL"
    image = models.ImageField(upload_to='products/attributes/%Y/%m/', blank=True, null=True)  # Ảnh option
    display_order = models.IntegerField(default=0)       # Thứ tự sắp xếp
    is_available = models.BooleanField(default=True)     # Còn sẵn có không
    created_at = models.DateTimeField(auto_now_add=True)

    # 🔄 Helper Methods
    def get_variants(self):              # Lấy tất cả variants có option này
    def get_available_combinations(self): # Lấy các kết hợp option khác còn sẵn
    @property
    def image_url(self):                 # URL ảnh option

# ===== IMAGE SYSTEM =====
class ProductImage(models.Model):
    """Ảnh sản phẩm với upload thực tế"""
    image_id = models.AutoField(primary_key=True)        # PK: 1, 2, 3...
    product = models.ForeignKey(Product, related_name='gallery_images')  # Sản phẩm
    image = models.ImageField(upload_to='products/gallery/%Y/%m/')       # Upload thật!
    is_thumbnail = models.BooleanField(default=False)    # Chỉ 1 thumbnail/product
    alt_text = models.CharField(max_length=200, blank=True, null=True)   # SEO alt text
    display_order = models.IntegerField(default=0)       # Thứ tự hiển thị
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def image_url(self):                # Trả về self.image.url
```

### **✨ Tính năng đã triển khai:**

✅ **Auto Generation**: Slug và model_code tự động tạo
✅ **Hierarchical Categories**: Cây danh mục vô hạn cấp
✅ **Complex Variant System**: JSON option_combinations linh hoạt
✅ **4-Type Attributes**: select, color, text, number
✅ **Real Image Upload**: ImageField với auto resize
✅ **Multi-seller Support**: Mỗi sản phẩm thuộc 1 seller
✅ **Rich Media Management**: Thumbnail + gallery system
✅ **Real-time Stock**: Tồn kho ở cấp variant
✅ **Flexible Pricing**: Base price + variant-specific pricing

---

## 🏷️ **CATEGORY - DANH MỤC SẢN PHẨM**

### **� Cấu trúc CategoryType**

```graphql
type CategoryType {
  # === THÔNG TIN CƠ BẢN ===
  categoryId: ID! # Primary key: "1", "2", "3"
  name: String! # "Giày thể thao", "Áo khoác"
  description: String # Mô tả chi tiết danh mục
  isActive: Boolean! # Trạng thái hoạt động
  createdAt: DateTime! # Thời gian tạo
  # === COMPUTED FIELDS ===
  fullPath: String! # "Thời trang > Giày dép > Giày thể thao"
  productCount: Int! # Số sản phẩm active trong danh mục
  thumbnailImage: String # Ảnh đại diện từ sản phẩm featured đầu tiên
  # === QUAN HỆ PHÂN CẤP ===
  parent: CategoryType # Danh mục cha (null nếu là root)
  subcategories: [CategoryType!]! # Danh sách danh mục con
  # === QUAN HỆ VỚI SẢN PHẨM ===
  products: ProductConnection # Sản phẩm trong danh mục (có pagination)
}
```

### **🔍 CATEGORY QUERIES - TRUY VẤN DANH MỤC**

#### **1️⃣ Lấy một danh mục cụ thể**

```graphql
query GetSingleCategory($id: ID!) {
  category(id: $id) {
    categoryId
    name
    description
    fullPath # "Thời trang > Giày dép > Giày thể thao"
    productCount # 125 sản phẩm
    thumbnailImage # URL ảnh đại diện
    isActive
    createdAt
    # Cây phân cấp
    parent {
      categoryId
      name
      fullPath
    }

    subcategories {
      categoryId
      name
      productCount

      # Có thể lấy thêm cấp con (nested)
      subcategories {
        categoryId
        name
        productCount
      }
    }

    # Sản phẩm trong danh mục (preview)
    products(first: 5) {
      edges {
        node {
          name
          minPrice
          thumbnailImage {
            imageUrl
          }
        }
      }
    }
  }
}
```

#### **3️⃣ Lấy cây danh mục hoàn chỉnh (3 cấp)**

```graphql
query GetCategoryTree {
  categories(
    filter: { isActive: true, parentId:null }
    sortBy: ""
  ) {
    edges {
      node {
        categoryId
        name
        productCount
        parent
        {
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
      }
    }

  }
}
```

#### **4️⃣ Tìm kiếm danh mục**

```graphql
query SearchCategories($searchTerm: String!) {
  categories(
    filter: {
      nameIcontains: $searchTerm # Tìm theo tên (không phân biệt hoa thường)
      isActive: true
      hasProducts: true # Chỉ danh mục có sản phẩm
    }
    sortBy: "product_count_desc" # Sắp xếp theo số sản phẩm nhiều nhất
    first: 10
  ) {
    edges {
      node {
        categoryId
        name
        fullPath
        productCount
        description

        # Top products trong danh mục
        products(first: 3, sortBy: "price_asc") {
          edges {
            node {
              name
              minPrice
              thumbnailImage {
                imageUrl
              }
            }
          }
        }
      }
    }
  }
}

# Variables:
# { "searchTerm": "giày" }
```

### **🔧 CATEGORY MUTATIONS - THAY ĐỔI DANH MỤC**

#### **1️⃣ Tạo danh mục mới**

```
mutation CreateCategory($input: CategoryCreateInput!) {
  categoryCreate(input: $input) {
    category {
      categoryId
      name
      description
      fullPath # "Giày thể thao > Giày chạy bộ"
      parent {
        categoryId
        name
      }

      productCount # 0 ban đầu
      thumbnailImage # null ban đầu
      createdAt
    }

    errors {
      message
      field
    }
  }
}

# Variables:
# {
#   "input": {
#     "name": "Giày chạy bộ",
#     "description": "Giày dành riêng cho chạy bộ và marathon",
#     "parentId": "1",              # ID của danh mục cha (nullable cho root)
#     "isActive": true
#   }
# }
```

#### **2️⃣ Cập nhật danh mục**

```graphql
mutation UpdateCategory($id: ID!, $input: CategoryUpdateInput!) {
  categoryUpdate(id: $id, input: $input) {
    category {
      categoryId
      name
      description
      fullPath # Sẽ thay đổi nếu đổi parent
      updatedAt

      parent {
        name
      }

      subcategories {
        name # Các danh mục con vẫn giữ nguyên
      }
    }

    errors {
      message
      field
    }
  }
}

# Variables:
# {
#   "id": "3",
#   "input": {
#     "name": "Giày chạy bộ cao cấp",
#     "description": "Giày chạy bộ chuyên nghiệp và cao cấp",
#     "parentId": "1",              # Có thể đổi parent
#     "isActive": true
#   }
# }
```

#### **3️⃣ Xóa danh mục**

```graphql
mutation DeleteCategory($id: ID!) {
  categoryDelete(id: $id) {
    success # true/false
    errors {
      message
      field
    }
  }
}

# Variables:
# { "id": "5" }
```

#### **4️⃣ Di chuyển danh mục sang parent mới**

```graphql
mutation MoveCategoryToNewParent($id: ID!, $newParentId: ID) {
  categoryUpdate(id: $id, input: { parentId: $newParentId }) {
    category {
      categoryId
      name
      fullPath # Đường dẫn sẽ thay đổi hoàn toàn
      parent {
        name
      }

      # Tất cả subcategories sẽ có fullPath mới
      subcategories {
        name
        fullPath
      }
    }

    errors {
      message
    }
  }
}

# Variables:
# {
#   "id": "10",
#   "newParentId": "3"              # Chuyển sang parent mới
# }
```

---

## 🛍️ **PRODUCT - SẢN PHẨM CHÍNH**

### **📊 Cấu trúc ProductType**

```graphql
type ProductType {
  # === THÔNG TIN CƠ BẢN ===
  productId: ID! # Primary key: "1", "2", "3"
  name: String! # "Nike Air Max 2024"
  slug: String! # "nike-air-max-2024" (auto-generated)
  description: String! # Mô tả HTML chi tiết
  brand: String # "Nike", "Adidas"
  modelCode: String! # "PRD-0001" (auto-generated)
  isActive: Boolean! # Hoạt động
  isFeatured: Boolean! # Nổi bật
  createdAt: DateTime! # Ngày tạo
  updatedAt: DateTime! # Ngày cập nhật
  # === GIÁ CẢ (COMPUTED TỪ VARIANTS) ===
  basePrice: Decimal! # Giá gốc
  minPrice: Decimal # Giá thấp nhất từ variants
  maxPrice: Decimal # Giá cao nhất từ variants
  priceRange: String # "1,000,000đ - 2,000,000đ"
  hasDiscount: Boolean # Có giảm giá không
  discountPercentage: Float # % giảm giá cao nhất
  # === THỐNG KÊ & TRẠNG THÁI ===
  totalStock: Int! # Tổng tồn kho từ variants
  variantCount: Int! # Số lượng variants
  availabilityStatus: String! # "in_stock", "low_stock", "out_of_stock"
  averageRating: Float # 4.5 (từ reviews)
  reviewCount: Int # 128 reviews
  totalSold: Int # Tổng số đã bán
  # === QUAN HỆ ===
  seller: UserType! # Người bán
  category: CategoryType! # Danh mục
  variants: ProductVariantConnection # Variants với pagination
  galleryImages: [ProductImageType!]! # Ảnh gallery
  thumbnailImage: ProductImageType # Ảnh đại diện
  attributeOptions: [ProductAttributeOptionType!]! # Tùy chọn thuộc tính
  # === NHÓM THUỘC TÍNH ===
  colorOptions: [ProductAttributeOptionType!]! # Màu sắc
  sizeOptions: [ProductAttributeOptionType!]! # Kích thước
  materialOptions: [ProductAttributeOptionType!]! # Chất liệu
}
```

### **🔍 PRODUCT QUERIES - TRUY VẤN SẢN PHẨM**

#### **1️⃣ Lấy một sản phẩm chi tiết**

```graphql
	
```

#### **2️⃣ Lấy danh sách sản phẩm với bộ lọc nâng cao**

```graphql
query GetProductsWithAdvancedFilter(
  $first: Int
  $after: String
  $filter: ProductFilterInput
  $sortBy: ProductSortingField
) {
  products(first: $first, after: $after, filter: $filter, sortBy: $sortBy) {
    edges {
      node {
        productId
        name
        slug
        brand
        minPrice
        maxPrice
        totalStock
        availabilityStatus
        averageRating
        reviewCount

        thumbnailImage {
          imageUrl
        }

        category {
          name
          fullPath
        }

        # Quick stats
        variantCount

        # Preview variants (top 3)
        variants(first: 3, sortBy: PRICE_ASC) {
          edges {
            node {
              sku
              price
              colorName
              sizeName
              isInStock
            }
          }
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

# Variables:
# {
#   "first": 20,
#   "after": null,
#   "filter": {
#     "search": "giày Nike",
#     "brand": "Nike",
#     "categoryId": "1",
#     "priceMin": 1000000,
#     "priceMax": 3000000,
#     "hasStock": true,
#     "isActive": true,
#     "isFeatured": null
#   },
#   "sortBy": "PRICE_ASC"
# }
```

#### **3️⃣ Sản phẩm nổi bật và mới**

```graphql
query GetSpecialProducts {
  # Sản phẩm nổi bật
  featuredProducts(first: 10) {
    edges {
      node {
        productId
        name
        brand
        minPrice
        averageRating

        thumbnailImage {
          imageUrl
        }

        category {
          name
        }

        # Stats
        totalStock
        variantCount
        totalSold
      }
    }
  }

  # Sản phẩm mới nhất
  products(filter: { isActive: true }, sortBy: "created_at_desc", first: 10) {
    edges {
      node {
        productId
        name
        brand
        createdAt
        minPrice

        thumbnailImage {
          imageUrl
        }

        # Badge "Mới"
        daysSinceCreated # Helper field
      }
    }
  }
}
```

#### **4️⃣ Sản phẩm theo danh mục**

```graphql
query GetProductsByCategory(
  $categoryId: ID!
  $first: Int
  $filter: ProductFilterInput
) {
  productsByCategory(
    categoryId: $categoryId
    first: $first
    filter: $filter
    sortBy: "price_asc"
  ) {
    edges {
      node {
        productId
        name
        brand
        minPrice
        maxPrice
        totalStock
        availabilityStatus

        thumbnailImage {
          imageUrl
        }

        # Category info (sẽ giống nhau vì cùng category)
        category {
          name
          fullPath
        }

        # Quick variant info
        colorOptions {
          value
          imageUrl
          variantCount
        }

        sizeOptions {
          value
          variantCount
        }
      }
    }

    totalCount
  }
}

# Variables:
# {
#   "categoryId": "1",
#   "first": 20,
#   "filter": {
#     "hasStock": true,
#     "isActive": true
#   }
# }
```

#### **5️⃣ Tìm kiếm sản phẩm thông minh**

```graphql
query SmartSearchProducts($query: String!, $first: Int) {
  searchProducts(
    query: $query # "nike air max black 39"
    filter: { isActive: true, hasStock: true }
    first: $first
  ) {
    edges {
      node {
        productId
        name
        brand
        minPrice

        # Search metadata
        searchScore # 0.95 (độ khớp với query)
        matchedFields # ["name", "brand"]
        highlightedName # "Nike <em>Air Max</em> 2024"
        highlightedDescription

        thumbnailImage {
          imageUrl
        }

        # Matching variants
        variants(
          filter: {
            colorName: "Black" # Nếu query có màu
            sizeName: "39" # Nếu query có size
            isActive: true
          }
        ) {
          edges {
            node {
              sku
              price
              colorName
              sizeName
              isInStock
            }
          }
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

# Variables:
# {
#   "query": "nike air max black 39",
#   "first": 20
# }
```

### **🔧 PRODUCT MUTATIONS - THAY ĐỔI SẢN PHẨM**

#### **1️⃣ Tạo sản phẩm mới**

```graphql
mutation CreateProduct($input: ProductCreateInput!) {
  productCreate(input: $input) {
    product {
      productId
      name
      slug # auto: "nike-air-max-2024"
      modelCode # auto: "PRD-0001", "PRD-0002", ...
      basePrice
      brand

      category {
        name
        fullPath
      }

      # Initial state
      minPrice # null ban đầu (chưa có variants)
      maxPrice # null ban đầu
      totalStock # 0 ban đầu
      variantCount # 0 ban đầu
      createdAt
    }

    errors {
      message
      field
    }
  }
}

# Variables:
# {
#   "input": {
#     "name": "Nike Air Max 2024",
#     "description": "Giày thể thao cao cấp với công nghệ Air Max mới nhất từ Nike",
#     "categoryId": "1",
#     "basePrice": "2500000",
#     "brand": "Nike",
#     "isActive": true,
#     "isFeatured": false
#   }
# }
```

#### **2️⃣ Cập nhật sản phẩm**

```graphql
mutation UpdateProduct($id: ID!, $input: ProductUpdateInput!) {
  productUpdate(id: $id, input: $input) {
    product {
      productId
      name
      basePrice
      isFeatured
      description
      updatedAt

      # Slug tự động cập nhật nếu đổi tên
      slug # "nike-air-max-2024-premium-edition"
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

# Variables:
# {
#   "id": "1",
#   "input": {
#     "name": "Nike Air Max 2024 Premium Edition",
#     "basePrice": "2700000",
#     "isFeatured": true,
#     "description": "Phiên bản cao cấp với chất liệu da thật và công nghệ mới nhất",
#     "categoryId": "2"              # Có thể đổi category
#   }
# }
```

# Variant đơn lẻ

productVariant(id: ID!) {
variantId
sku
price
stock
weight
optionCombinations # JSON
colorName # từ optionCombinations
sizeName # từ optionCombinations
isInStock # computed
colorImageUrl # từ color option
isActive

    product { name }

}

#### **3️⃣ Xóa sản phẩm**

```graphql
mutation DeleteProduct($id: ID!) {
  productDelete(id: $id) {
    success # true/false
    errors {
      message
      field
    }
  }
}

# Variables:
# { "id": "1" }
```

#### **4️⃣ Tạo hàng loạt sản phẩm**

```graphql
mutation BulkCreateProducts($products: [ProductCreateInput!]!) {
  bulkProductCreate(products: $products) {
    products {
      productId
      name
      slug # Tự động tạo cho mỗi sản phẩm
      modelCode # PRD-0002, PRD-0003, PRD-0004
      brand
      basePrice

      category {
        name
      }
    }

    successCount # Số sản phẩm tạo thành công
    errors {
      message
      productIndex # Sản phẩm thứ mấy bị lỗi
    }
  }
}

# Variables:
# {
#   "products": [
#     {
#       "name": "Adidas Ultraboost 2024",
#       "categoryId": "1",
#       "basePrice": "3200000",
#       "brand": "Adidas",
#       "description": "Giày chạy bộ cao cấp từ Adidas"
#     },
#     {
#       "name": "Puma RS-X Future",
#       "categoryId": "1",
#       "basePrice": "2800000",
#       "brand": "Puma",
#       "description": "Giày thể thao retro-futuristic"
#     }
#   ]
# }
```

---

## 🎨 **PRODUCT VARIANT - BIẾN THỂ**

### **📊 Cấu trúc ProductVariantType**

```graphql
type ProductVariantType {
  # === THÔNG TIN CƠ BẢN ===
  variantId: ID! # Primary key: "1", "2", "3"
  sku: String! # "NIKE-AIR-MAX-39-BLACK"
  price: Decimal! # Giá cụ thể của variant
  stock: Int! # Tồn kho
  weight: Decimal! # Trọng lượng (kg)
  isActive: Boolean! # Hoạt động
  createdAt: DateTime! # Ngày tạo
  updatedAt: DateTime! # Ngày cập nhật
  # === THUỘC TÍNH (Parsed từ JSON) ===
  optionCombinations: JSONString! # {"Size": "39", "Color": "Black"}
  colorName: String # "Black" - parsed từ JSON
  sizeName: String # "39" - parsed từ JSON
  materialName: String # "Leather" - parsed từ JSON
  # === COMPUTED FIELDS ===
  isInStock: Boolean! # stock > 0 && is_active
  stockStatus: String! # "in_stock", "low_stock", "out_of_stock"
  discountPercentage: Float # % giảm giá so với basePrice
  colorImageUrl: String # URL ảnh màu từ attribute option
  # === QUAN HỆ ===
  product: ProductType! # Sản phẩm cha
  colorImage: ProductAttributeOptionType # Ảnh màu tương ứng
}
```

### **🔍 VARIANT QUERIES - TRUY VẤN BIẾN THỂ**

#### **1️⃣ Lấy variants của một sản phẩm**

```graphql
query GetProductVariants($productId: ID!, $filter: ProductVariantFilterInput) {
  productVariants(
    filter: {
      productId: $productId
      isActive: true
      ...filter
    }
    sortBy: PRICE_ASC
  ) {
    edges {
      node {
        variantId
        sku
        price
        stock
        weight

        # Thuộc tính từ JSON
        colorName
        sizeName
        materialName
        colorImageUrl

        # Trạng thái
        isInStock
        stockStatus
        discountPercentage

        # Sản phẩm cha
        product {
          name
          brand
          basePrice
        }
      }
    }
  }
}

# Variables:
# {
#   "productId": "1",
#   "filter": {
#     "hasStock": true,
#     "priceMin": 2000000,
#     "priceMax": 3000000
#   }
# }
```

### **🔧 VARIANT MUTATIONS - THAY ĐỔI BIẾN THỂ**

#### **1️⃣ Tạo variant mới**

```graphql
mutation CreateVariant($input: ProductVariantCreateInput!) {
  productVariantCreate(input: $input) {
    productVariant {
      variantId
      sku
      price
      stock
      colorName # "Black" - parsed từ JSON
      sizeName # "39" - parsed từ JSON
      isInStock # true vì stock > 0
      stockStatus # "in_stock"
      product {
        name
        # Các computed fields sẽ tự động cập nhật
        minPrice # Cập nhật nếu đây là giá thấp nhất
        maxPrice # Cập nhật nếu đây là giá cao nhất
        totalStock # Tăng thêm stock của variant này
      }
    }

    errors {
      message
      field
    }
  }
}

# Variables:
# {
#   "input": {
#     "productId": "1",
#     "sku": "NIKE-AIR-MAX-2024-39-BLACK",
#     "price": "2650000",
#     "stock": 50,
#     "weight": "0.8",
#     "optionCombinations": "{\"Size\": \"39\", \"Color\": \"Black\"}",
#     "isActive": true
#   }
# }
```

#### **2️⃣ Cập nhật stock & price**

```graphql
mutation UpdateStock($variantId: ID!, $stock: Int!) {
  stockUpdate(variantId: $variantId, stock: $stock) {
    productVariant {
      sku
      stock
      isInStock # Có thể thay đổi từ true → false
      stockStatus # "low_stock" nếu <= 5
      product {
        totalStock # Tự động cập nhật
        availabilityStatus # Có thể thay đổi
      }
    }

    errors {
      message
    }
  }
}

# Variables:
# {
#   "variantId": "1",
#   "stock": 25
# }
```

```graphql
mutation UpdatePrice($variantId: ID!, $price: Decimal!) {
  priceUpdate(variantId: $variantId, price: $price) {
    productVariant {
      sku
      price
      discountPercentage # So với basePrice
      product {
        minPrice # Có thể thay đổi
        maxPrice # Có thể thay đổi
        priceRange # Tự động cập nhật
      }
    }

    errors {
      message
    }
  }
}

# Variables:
# {
#   "variantId": "1",
#   "price": "2800000"
# }
```

#### **3️⃣ Bulk operations cho variants**

```graphql
mutation BulkUpdateStock($updates: [StockUpdateInput!]!) {
  bulkStockUpdate(updates: $updates) {
    results {
      productVariant {
        sku
        stock
        stockStatus
        isInStock
      }
      success
      errors {
        message
      }
    }

    successCount # Số lượng update thành công
    failedCount # Số lượng failed
  }
}

# Variables:
# {
#   "updates": [
#     { "variantId": "1", "stock": 20 },
#     { "variantId": "2", "stock": 35 },
#     { "variantId": "3", "stock": 0 }     # Out of stock
#   ]
# }
```

---

## 🖼️ **IMAGE SYSTEM - HỆ THỐNG ẢNH**

### **📊 Cấu trúc ProductImageType**

```graphql
type ProductImageType {
  imageId: ID! # Primary key
  imageUrl: String! # http://localhost:8000/media/products/gallery/2025/10/image.jpg
  isThumbnail: Boolean! # Chỉ 1 ảnh thumbnail/product
  altText: String # SEO alt text
  displayOrder: Int! # Thứ tự hiển thị
  createdAt: DateTime! # Ngày upload
  product: ProductType! # Sản phẩm chủ sở hữu
}
```

### **📤 IMAGE MUTATIONS - UPLOAD & QUẢN LÝ ẢNH**

#### **1️⃣ Upload ảnh sản phẩm**

```graphql
# Chú ý: Cần sử dụng multipart form data
mutation UploadProductImage(
  $productId: ID!
  $image: Upload!
  $isThumbnail: Boolean
) {
  uploadProductImage(
    productId: $productId
    image: $image # File upload thực tế
    isThumbnail: $isThumbnail # Chỉ 1 ảnh thumbnail/product
    altText: "Ảnh Nike Air Max 2024"
    displayOrder: 0
  ) {
    productImage {
      imageId
      imageUrl # http://localhost:8000/media/products/gallery/2025/10/nike_air_max.jpg
      isThumbnail
      altText
      displayOrder
      createdAt

      product {
        name
        # Nếu là thumbnail, product.thumbnailImage sẽ cập nhật
      }
    }

    errors {
      message
    }
  }
}

# Variables (trong GraphQL Playground):
# {
#   "productId": "1",
#   "isThumbnail": true
# }
# File: Chọn file ảnh trong GraphQL Playground
```

#### **2️⃣ Upload ảnh cho attribute option (màu sắc)**

```graphql
mutation UploadAttributeOptionImage($optionId: ID!, $image: Upload!) {
  uploadAttributeOptionImage(optionId: $optionId, image: $image) {
    attributeOption {
      optionId
      value # "Black"
      valueCode # "#000000"
      imageUrl # http://localhost:8000/media/products/attributes/2025/10/black_color.jpg
      attribute {
        name # "Color"
        type # "color"
        hasImage # true
      }

      # Variants sử dụng option này sẽ có colorImageUrl
      variantCount
    }

    errors {
      message
    }
  }
}

# Variables:
# {
#   "optionId": "5"                 # ID của color option "Black"
# }
# File: Chọn file ảnh màu đen
```

#### **3️⃣ Xóa ảnh**

```graphql
mutation DeleteProductImage($imageId: ID!) {
  deleteProductImage(imageId: $imageId) {
    success # File sẽ tự động xóa khỏi storage
    errors {
      message
    }
  }
}

# Variables:
# { "imageId": "img_123" }
```

#### **4️⃣ Cập nhật thứ tự ảnh**

```graphql
mutation ReorderProductImages(
  $productId: ID!
  $imageOrders: [ImageOrderInput!]!
) {
  reorderProductImages(productId: $productId, imageOrders: $imageOrders) {
    productImages {
      imageId
      imageUrl
      displayOrder # Thứ tự mới
      isThumbnail
    }

    errors {
      message
    }
  }
}

# Variables:
# {
#   "productId": "1",
#   "imageOrders": [
#     { "imageId": "img_1", "displayOrder": 0 },
#     { "imageId": "img_2", "displayOrder": 1 },
#     { "imageId": "img_3", "displayOrder": 2 }
#   ]
# }
```

---

## 🔍 **ADVANCED FEATURES - TÍNH NĂNG NÂNG CAO**

### **🎯 Filtering System - Hệ thống lọc**

```graphql
# === INPUT TYPES CHO FILTERING ===
input ProductFilterInput {
  # 🔤 Text Search
  search: String # Tìm trong name, description, brand
  name: String # Exact match tên
  nameIcontains: String # Contains (case-insensitive)
  brand: String # Exact brand
  brandIn: [String!] # Multi-brand: ["Nike", "Adidas"]
  modelCode: String # Exact model code
  # 🏷️ Category & Seller
  categoryId: ID # Thuộc danh mục cụ thể
  categoryIdIn: [ID!] # Multi-category
  includeSubcategories: Boolean # Bao gồm danh mục con
  sellerId: ID # Của seller cụ thể
  sellerIdIn: [ID!] # Multi-seller
  # 💰 Price Filtering
  priceMin: Decimal # Giá tối thiểu (từ variants)
  priceMax: Decimal # Giá tối đa (từ variants)
  basePriceMin: Decimal # Base price tối thiểu
  basePriceMax: Decimal # Base price tối đa
  hasDiscount: Boolean # Có giảm giá
  discountMin: Float # % giảm giá tối thiểu
  # 📦 Stock & Availability
  hasStock: Boolean # Có tồn kho (từ variants)
  stockMin: Int # Tồn kho tối thiểu
  stockMax: Int # Tồn kho tối đa
  hasVariants: Boolean # Có variants
  hasImages: Boolean # Có ảnh
  # 🏃 Status Filtering
  isActive: Boolean # Sản phẩm đang hoạt động
  isFeatured: Boolean # Sản phẩm nổi bật
  availabilityStatus: String # "in_stock", "low_stock", "out_of_stock"
  # 🎨 Attribute Filtering
  attributes: [AttributeFilterInput!] # Lọc theo thuộc tính
  colorName: String # Có variant màu này
  colorNameIn: [String!] # Multi-color
  sizeName: String # Có variant size này
  sizeNameIn: [String!] # Multi-size
  # 📅 Date Filtering
  createdAfter: DateTime # Tạo sau ngày
  createdBefore: DateTime # Tạo trước ngày
  updatedAfter: DateTime # Cập nhật sau ngày
  updatedBefore: DateTime # Cập nhật trước ngày
  # ⭐ Rating & Reviews
  ratingMin: Float # Rating tối thiểu
  ratingMax: Float # Rating tối đa
  hasReviews: Boolean # Có reviews
  reviewCountMin: Int # Số review tối thiểu
}

input AttributeFilterInput {
  name: String! # "Color", "Size", "Material"
  values: [String!]! # ["Black", "White", "Red"]
  operator: AttributeOperator # AND, OR (default: OR)
}

enum AttributeOperator {
  AND # Phải có tất cả values
  OR # Có ít nhất 1 value
}

# === SORTING OPTIONS ===
enum ProductSortingField {
  NAME # A-Z
  NAME_DESC # Z-A
  PRICE # Giá thấp → cao (từ minPrice)
  PRICE_DESC # Giá cao → thấp (từ maxPrice)
  CREATED_AT # Cũ → mới
  CREATED_AT_DESC # Mới → cũ (default)
  UPDATED_AT # Ít update → nhiều update
  UPDATED_AT_DESC # Nhiều update → ít update
  STOCK # Ít hàng → nhiều hàng
  STOCK_DESC # Nhiều hàng → ít hàng
  RATING # Rating thấp → cao
  RATING_DESC # Rating cao → thấp
  SALES # Bán ít → bán nhiều
  SALES_DESC # Bán nhiều → bán ít
  FEATURED # Non-featured → featured
  FEATURED_DESC # Featured → non-featured
}
```

### **📊 Analytics & Statistics - Thống kê**

```graphql
query GetProductAnalytics {
  productStats {
    # === TỔNG QUAN ===
    totalProducts # 1,234
    totalVariants # 5,678
    totalCategories # 45
    activeProducts # 1,100
    featuredProducts # 56
    # === GIÁ CẢ ===
    averagePrice # 2,500,000
    totalValue # Tổng giá trị kho
    priceRanges {
      range # "1-2 triệu"
      min
      max
      count # Số sản phẩm trong khoảng
    }

    # === TỒN KHO ===
    totalStock # 12,345
    averageStock # 25
    lowStockProducts # 23 (stock <= 5)
    outOfStockProducts # 12
    # === TOP PERFORMERS ===
    topSellingProducts(limit: 10) {
      product {
        name
        brand
        minPrice
      }
      soldCount
      revenue
    }

    topRatedProducts(limit: 10) {
      product {
        name
        brand
      }
      averageRating
      reviewCount
    }

    # === ALERTS ===
    stockAlerts {
      product {
        name
      }
      variant {
        sku
      }
      currentStock
      alertLevel # "low", "critical", "out"
    }

    # === CATEGORY BREAKDOWN ===
    categoryStats {
      category {
        name
        fullPath
      }
      productCount
      totalStock
      averagePrice
      totalValue
    }

    # === BRAND BREAKDOWN ===
    brandStats {
      brandName
      productCount
      averagePrice
      totalValue
    }
  }
}
```

### **🚀 Real-time Subscriptions - Theo dõi thời gian thực**

```graphql
# === THEO DÕI THAY ĐỔI STOCK ===
subscription ProductStockUpdates($productIds: [ID!]) {
  stockUpdates(productIds: $productIds) {
    variant {
      variantId
      sku
      stock
      stockStatus
      isInStock

      product {
        name
        totalStock
        availabilityStatus
      }
    }

    changeType # "STOCK_UPDATE", "LOW_STOCK", "OUT_OF_STOCK", "BACK_IN_STOCK"
    previousStock
    newStock
    timestamp
  }
}

# === THEO DÕI THAY ĐỔI GIÁ ===
subscription ProductPriceUpdates($productIds: [ID!]) {
  priceUpdates(productIds: $productIds) {
    product {
      productId
      name
      minPrice
      maxPrice
      priceRange
    }

    variant {
      variantId
      sku
      price
    }

    changeType # "PRICE_INCREASE", "PRICE_DECREASE", "DISCOUNT_APPLIED"
    previousPrice
    newPrice
    changePercentage # +15% or -20%
    timestamp
  }
}

# === THEO DÕI SẢN PHẨM MỚI ===
subscription NewProducts($categoryId: ID, $sellerId: ID) {
  newProducts(categoryId: $categoryId, sellerId: $sellerId) {
    product {
      productId
      name
      brand
      minPrice

      thumbnailImage {
        imageUrl
      }

      category {
        name
      }

      seller {
        username
      }
    }

    timestamp
  }
}
```

---

## 🔧 **SETUP & INTEGRATION**

### **✅ Tích hợp hoàn tất**

#### **1. GraphQL Schema đã sẵn sàng**

```python
# graphql/api.py - ✅ ĐÃ SETUP
import graphene
from .product.schema import ProductQueries, ProductMutations

class Query(ProductQueries, graphene.ObjectType):
    health = graphene.String()
    def resolve_health(self, info):
        return "SHOEX GraphQL API is running!"

class Mutation(ProductMutations, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)
```

#### **2. Django Settings đã cấu hình**

```python
# config/settings.py - ✅ ĐÃ SETUP
INSTALLED_APPS = [
    'graphene_django',              # GraphQL core
    'graphene_file_upload',         # Image upload support
    'products',                     # Product models
    # ...
]

GRAPHENE = {
    "SCHEMA": "graphql.api.schema",
    'MIDDLEWARE': [
        'graphene_file_upload.django.FileUploadGraphQLMiddleware',
    ],
}

# Media files - ✅ ĐÃ SETUP
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

#### **3. URLs đã cấu hình**

```python
# config/urls.py - ✅ ĐÃ SETUP
from graphene_django.views import GraphQLView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('graphql/', GraphQLView.as_view(graphiql=True, schema=schema)),
]

# Media serving - ✅ ĐÃ SETUP
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

#### **4. Database đã migrate**

```bash
# ✅ ĐÃ CHẠY
python manage.py makemigrations products
python manage.py migrate products
```

#### **5. Server sẵn sàng**

```bash
# ✅ ĐANG CHẠY
python manage.py runserver
# GraphQL Playground: http://127.0.0.1:8000/graphql/
```

---

## 📊 **PERFORMANCE & SECURITY**

### **⚡ Performance Optimization**

- **DataLoader**: Batch loading cho N+1 queries
- **Database Indexing**: Index trên `slug`, `brand`, `sku`, `category_id`
- **Query Complexity**: Giới hạn depth và field selections
- **Caching Strategy**: Redis cache cho product lists, categories
- **Image Optimization**: Auto resize, WebP conversion
- **Search Performance**: PostgreSQL full-text search

### **🔒 Security Measures**

- **Authentication**: JWT-based với refresh tokens
- **Authorization**: Permission-based field access
- **Rate Limiting**: GraphQL query complexity scoring
- **Input Validation**: Sanitize uploads và text inputs
- **CORS Configuration**: Strict origin policies

### **📈 Monitoring & Analytics**

- **Query Performance**: Slow query detection
- **Error Tracking**: Comprehensive error logging
- **Business Metrics**: Sales, inventory, user behavior
- **Real-time Alerts**: Stock levels, performance issues

---

## 🎯 **BEST PRACTICES - THỰC HÀNH TỐT NHẤT**

1. **🎨 Variant Strategy**: Luôn tạo variants cho sản phẩm có tùy chọn
2. **📋 Attribute Planning**: Thiết kế attributes trước khi tạo products
3. **🖼️ Image Optimization**: Tối ưu ảnh và sử dụng CDN
4. **🔍 Search Optimization**: Full-text search cho performance
5. **📦 Stock Management**: Cập nhật stock real-time
6. **🏗️ Category Structure**: Cây danh mục hợp lý, không quá sâu
7. **🔄 Bulk Operations**: Sử dụng bulk mutations cho admin tasks
8. **📊 Analytics**: Monitor performance và business metrics

---

## 🔗 **MODULE LIÊN QUAN**

- **👤 User Module**: Seller management, product ownership
- **🛒 Cart Module**: Product variants trong giỏ hàng
- **📦 Order Module**: Product fulfillment, inventory tracking
- **⭐ Review Module**: Product ratings, reviews
- **🎫 Discount Module**: Product promotions, coupons
- **🚚 Shipping Module**: Product weight, dimensions
- **🔔 Notification Module**: Stock alerts, price changes

---

**🚀 SHOEX GraphQL Product API - Production Ready!**
_Hệ thống Product & Variant phức tạp với Image Upload thực tế_
_Theo kiến trúc Django + Graphene hiện đại_ ✅

```

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
