# Module Cart - GraphQL API

Module quản lý giỏ hàng và wishlist GraphQL toàn diện cho nền tảng thương mại điện tử SHOEX theo mẫu kiến trúc Django-Graphene với **Hỗ trợ Guest User & Session Management**.

## 📁 Cấu trúc Module

```
graphql_api/cart/
├── __init__.py                 # Xuất module
├── schema.py                   # Schema GraphQL chính
├── README.md                   # Tài liệu này
├── types/
│   ├── __init__.py
│   └── cart.py                 # Các kiểu GraphQL (CartType, CartItemType, WishlistType)
├── mutations/
│   ├── __init__.py
│   └── cart_mutations.py       # Mutations CRUD
├── filters/
│   ├── __init__.py
│   └── cart_filters.py         # Lọc và sắp xếp
├── dataloaders/
│   ├── __init__.py
│   └── cart_loaders.py         # Tối ưu hóa truy vấn N+1
└── bulk_mutations/
    ├── __init__.py
    └── cart_bulk_mutations.py   # Thao tác hàng loạt
```

## 🎯 Cart Model Integration

Module này tích hợp với các models Cart của SHOEX (`cart/models.py`):

```python
class Cart(models.Model):
    """Giỏ hàng hỗ trợ cả user đã đăng nhập và guest user"""
    user = models.OneToOneField(User, null=True, blank=True)  # Cho user đã đăng nhập
    session_key = models.CharField(max_length=40, null=True)  # Cho guest user
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)  # Hết hạn cho guest

class CartItem(models.Model):
    """Sản phẩm trong giỏ hàng"""
    cart = models.ForeignKey(Cart, related_name='items')
    variant = models.ForeignKey('products.ProductVariant')
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)  # Giá tại thời điểm thêm
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Wishlist(models.Model):
    """Danh sách yêu thích (chỉ cho user đã đăng nhập)"""
    user = models.ForeignKey(User, related_name='wishlist_items')
    variant = models.ForeignKey('products.ProductVariant')
    created_at = models.DateTimeField(auto_now_add=True)
```

### Các tính năng quan trọng:

- **Dual Cart System**: Hỗ trợ cả user đã đăng nhập và guest user
- **Session Management**: Quản lý giỏ hàng qua session cho guest
- **Cart Merging**: Gộp giỏ hàng guest vào user cart khi đăng nhập
- **Price Tracking**: Lưu giá tại thời điểm thêm vào giỏ, so sánh với giá hiện tại
- **Stock Validation**: Kiểm tra tồn kho khi thêm/cập nhật
- **Auto Expiration**: Tự động hết hạn giỏ hàng guest

## 🚀 Tính năng

### Kiểu GraphQL

- **CartType**: Thông tin giỏ hàng với các phép tính tổng hợp
- **CartItemType**: Chi tiết sản phẩm trong giỏ hàng
- **WishlistType**: Sản phẩm trong danh sách yêu thích
- **CartSummary**: Tóm tắt thông tin giỏ hàng
- **WishlistSummary**: Tóm tắt thông tin wishlist
- **Cart/CartItem/WishlistConnection**: Hỗ trợ phân trang

### Truy vấn (Queries)

```graphql
# Giỏ hàng của user hiện tại hoặc guest
myCart(sessionKey: String): CartType
cart(id: ID!): CartType

# Items trong giỏ hàng
cartItems(cartId: ID, filter: CartItemFilterInput): CartItemConnection
myCartItems: CartItemConnection

# Wishlist
myWishlist: WishlistConnection
wishlistItem(id: ID!): WishlistType

# Tóm tắt
cartSummary(sessionKey: String): CartSummary
wishlistSummary: WishlistSummary

# Thống kê
totalCartItems(sessionKey: String): Int
totalWishlistItems: Int
cartValue(sessionKey: String): Decimal
```

### Thay đổi (Mutations)

```graphql
# Quản lý giỏ hàng
addToCart(input: CartItemInput!, sessionKey: String): AddToCart
updateCartItem(itemId: ID!, quantity: Int!): UpdateCartItem
removeFromCart(itemId: ID!): RemoveFromCart
clearCart(sessionKey: String): ClearCart
mergeCart(sessionKey: String!): MergeCart

# Quản lý wishlist
addToWishlist(input: WishlistItemInput!): AddToWishlist
removeFromWishlist(wishlistId: ID!): RemoveFromWishlist
moveToCartFromWishlist(wishlistId: ID!, quantity: Int): MoveToCartFromWishlist
clearWishlist: ClearWishlist

# Thao tác hàng loạt
bulkAddToCart(items: [CartItemInput!]!, sessionKey: String): BulkAddToCart
bulkUpdateCartItems(updates: [CartItemUpdateInput!]!): BulkUpdateCartItems
bulkRemoveFromCart(itemIds: [ID!]!): BulkRemoveFromCart
```

### Lọc & Sắp xếp

```graphql
input CartFilterInput {
  # Lọc theo user/session
  user: ID
  sessionKey: String

  # Lọc theo thời gian
  createdAfter: DateTime
  createdBefore: DateTime

  # Lọc theo trạng thái
  isExpired: Boolean
  hasItems: Boolean
  totalAmountMin: Decimal
  totalAmountMax: Decimal
}

input CartItemFilterInput {
  # Lọc theo cart
  cart: ID
  cartUser: ID

  # Lọc theo sản phẩm
  variant: ID
  product: ID
  category: ID

  # Lọc theo giá/số lượng
  unitPriceMin: Decimal
  unitPriceMax: Decimal
  quantityMin: Int
  quantityMax: Int

  # Lọc theo trạng thái
  priceChanged: Boolean
  isAvailable: Boolean
}

input WishlistFilterInput {
  user: ID
  variant: ID
  product: ID
  category: ID
  createdAfter: DateTime
  createdBefore: DateTime
  isAvailable: Boolean
  isInStock: Boolean
}
```

### DataLoaders (Tối ưu hóa N+1)

- `CartLoader`: Tải giỏ hàng theo batch theo ID
- `CartByUserLoader`: Tải giỏ hàng theo user
- `CartBySessionLoader`: Tải giỏ hàng theo session key
- `CartItemLoader`: Tải cart items theo batch
- `CartItemsByCartLoader`: Tải items theo cart
- `WishlistLoader`: Tải wishlist items theo batch
- `WishlistByUserLoader`: Tải wishlist theo user
- `CartStatsLoader`: Tải thống kê giỏ hàng
- `WishlistStatsLoader`: Tải thống kê wishlist

## 🔧 Tích hợp

### 1. Thêm vào Schema GraphQL chính

Trong `graphql_api/schema.py`:

```python
from .cart.schema import CartQuery, CartMutation

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

### 2. Thiết lập Session Management

Trong Django settings:

```python
# Bật sessions
MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    # ... other middleware
]

# Cấu hình session
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 30 * 24 * 60 * 60  # 30 days for guest carts
```

### 3. Context và Authentication

```python
class GraphQLView(GraphQLView):
    def get_context(self, request):
        context = super().get_context(request)
        context.session = request.session
        return context
```

## 📝 Ví dụ sử dụng

### Ví dụ Truy vấn

```graphql
# Lấy giỏ hàng của user hiện tại
query MyCart {
  myCart {
    id
    totalItems
    totalAmount
    totalWeight
    isExpired
    createdAt
    updatedAt

    items {
      edges {
        node {
          id
          quantity
          unitPrice
          subtotal
          currentPrice
          priceChanged
          isAvailable
          maxQuantity

          variant {
            id
            sku
            price
            stock
            product {
              name
              brand
            }
          }
        }
      }
    }
  }
}

# Lấy giỏ hàng guest với session key
query GuestCart($sessionKey: String!) {
  myCart(sessionKey: $sessionKey) {
    id
    totalItems
    totalAmount
    items {
      edges {
        node {
          id
          quantity
          unitPrice
          variant {
            id
            sku
            product {
              name
            }
          }
        }
      }
    }
  }
}

# Lấy wishlist
query MyWishlist {
  myWishlist {
    edges {
      node {
        id
        createdAt
        isAvailable
        currentPrice
        isInStock

        variant {
          id
          sku
          price
          stock
          product {
            name
            brand
          }
        }
      }
    }
    totalCount
  }
}

# Tóm tắt giỏ hàng
query CartSummary {
  cartSummary {
    totalItems
    totalAmount
    totalWeight
    itemCount
    hasUnavailableItems
    hasPriceChanges
  }
}
```

### Ví dụ Mutations

```graphql
# Thêm sản phẩm vào giỏ hàng (user đã đăng nhập)
mutation AddToCart {
  addToCart(input: { variantId: "1", quantity: 2 }) {
    success
    cartItem {
      id
      quantity
      subtotal
      variant {
        sku
        product {
          name
        }
      }
    }
    cart {
      totalItems
      totalAmount
    }
    errors
  }
}

# Thêm sản phẩm vào giỏ hàng guest
mutation AddToGuestCart($sessionKey: String!) {
  addToCart(input: { variantId: "1", quantity: 1 }, sessionKey: $sessionKey) {
    success
    cartItem {
      id
      quantity
      subtotal
    }
    errors
  }
}

# Cập nhật số lượng
mutation UpdateCartItem {
  updateCartItem(itemId: "1", quantity: 3) {
    success
    cartItem {
      id
      quantity
      subtotal
    }
    errors
  }
}

# Gộp giỏ hàng khi user đăng nhập
mutation MergeCart($sessionKey: String!) {
  mergeCart(sessionKey: $sessionKey) {
    success
    cart {
      id
      totalItems
      totalAmount
      items {
        edges {
          node {
            id
            quantity
            variant {
              sku
            }
          }
        }
      }
    }
    errors
  }
}

# Thêm vào wishlist
mutation AddToWishlist {
  addToWishlist(input: { variantId: "1" }) {
    success
    wishlistItem {
      id
      createdAt
      variant {
        sku
        product {
          name
        }
      }
    }
    errors
  }
}

# Chuyển từ wishlist vào giỏ hàng
mutation MoveToCartFromWishlist {
  moveToCartFromWishlist(wishlistId: "1", quantity: 2) {
    success
    cartItem {
      id
      quantity
      subtotal
    }
    errors
  }
}
```

## 🔒 Xác thực & Quyền

- **Guest Users**: Có thể quản lý giỏ hàng thông qua session key
- **Authenticated Users**: Truy cập đầy đủ cart và wishlist
- **Cart Ownership**: User chỉ có thể truy cập giỏ hàng của mình
- **Session Validation**: Kiểm tra session key hợp lệ cho guest
- **Stock Validation**: Kiểm tra tồn kho trước khi thêm/cập nhật
- **Price Validation**: Cảnh báo khi giá thay đổi

## 🎯 Thực hành tốt nhất

1. **Session Management**: Luôn tạo session key cho guest user và lưu trữ phía client
2. **Cart Merging**: Tự động gộp giỏ hàng khi user đăng nhập
3. **Stock Validation**: Kiểm tra tồn kho real-time trước khi checkout
4. **Price Tracking**: Hiển thị cảnh báo khi giá sản phẩm thay đổi
5. **Auto Cleanup**: Định kỳ xóa giỏ hàng guest đã hết hạn
6. **Error Handling**: Xử lý graceful khi sản phẩm không còn bán

## 🔗 Các Module liên quan

- **Product Module**: Tích hợp với ProductVariant để kiểm tra tồn kho, giá
- **User Module**: Quản lý giỏ hàng của user đã đăng nhập
- **Order Module**: Chuyển đổi cart thành order khi checkout
- **Discount Module**: Áp dụng mã giảm giá cho cart

## 📊 Cân nhắc về hiệu suất

- **DataLoaders**: Giảm truy vấn N+1 khi load cart items và variants
- **Caching**: Cache cart summary để tránh tính toán lại
- **Indexing**: Index trên user_id, session_key, variant_id
- **Batch Operations**: Sử dụng bulk operations cho thao tác nhiều items
- **Expired Cart Cleanup**: Background task để dọn dẹp cart hết hạn

## 🧪 Kiểm thử & Xác thực

### Testing Steps

1. **Setup Database**:

   ```bash
   python manage.py makemigrations cart
   python manage.py migrate
   ```

2. **Test Guest Cart**:

   ```python
   # Test thêm sản phẩm vào guest cart
   session_key = "test_session_123"
   # Sử dụng GraphQL mutations với session_key
   ```

3. **Test User Cart**:

   ```python
   # Test với user đã đăng nhập
   # Test cart merging khi login
   ```

4. **Test Wishlist**:
   ```python
   # Test wishlist chỉ cho authenticated user
   # Test move từ wishlist vào cart
   ```

### Kết quả mong đợi

- ✅ Guest user có thể quản lý giỏ hàng qua session
- ✅ User cart được gộp đúng cách khi đăng nhập
- ✅ Stock validation hoạt động chính xác
- ✅ Price changes được detect và hiển thị
- ✅ Wishlist chỉ hoạt động cho authenticated user
- ✅ Cart expiration hoạt động cho guest cart

### Danh sách kiểm tra tích hợp

- [x] CartType với các trường tính toán
- [x] Session-based cart cho guest user
- [x] Cart merging functionality
- [x] Stock validation trong mutations
- [x] Price change detection
- [x] Wishlist functionality
- [x] Bulk operations
- [x] DataLoaders tối ưu hóa
- [x] Filters và sorting
- [x] Error handling toàn diện

---

**Được tạo cho Nền tảng Thương mại Điện tử SHOEX**
_Hỗ trợ Guest User & Session Management_ ✅
_Theo mẫu kiến trúc Django-Graphene_
