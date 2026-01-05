# Cart GraphQL API Examples

## Queries

### 1. Lấy giỏ hàng của user hiện tại
```graphql
query MyCart {
  myCart {
    cartId
    totalItems
    totalAmount
    totalWeight
    createdAt
    updatedAt
    items {
      itemId
      quantity
      unitPrice
      subtotal
      variant {
        variantId
        colorName
        sizeName
        price
        finalPrice
        stock
        product {
          productId
          name
          thumbnailImage {
            imageUrl
          }
        }
      }
    }
  }
}
```

### 2. Lấy danh sách items trong giỏ hàng
```graphql
query CartItems {
  cartItems {
    itemId
    quantity
    unitPrice
    subtotal
    variant {
      variantId
      colorName
      sizeName
      stock
      product {
        name
        basePrice
      }
    }
  }
}
```

## Mutations

### 1. Thêm sản phẩm vào giỏ hàng
```graphql
mutation AddToCart {
  addToCart(input: {
    variantId: "1"
    quantity: 2
  }) {
    success
    errors
    cart {
      cartId
      totalItems
      totalAmount
    }
    cartItem {
      itemId
      quantity
      unitPrice
      subtotal
    }
  }
}
```

### 2. Xóa sản phẩm khỏi giỏ hàng
```graphql
mutation RemoveFromCart {
  removeFromCart(input: {
    itemId: "1"
  }) {
    success
    errors
    cart {
      cartId
      totalItems
      totalAmount
    }
  }
}
```

### 3. Cập nhật số lượng sản phẩm
```graphql
mutation UpdateCartItemQuantity {
  updateCartItemQuantity(input: {
    itemId: "1"
    quantity: 5
  }) {
    success
    errors
    cartItem {
      itemId
      quantity
      unitPrice
      subtotal
    }
  }
}
```

### 4. Xóa tất cả sản phẩm trong giỏ hàng
```graphql
mutation ClearCart {
  clearCart(input: {}) {
    success
    errors
    cart {
      cartId
      totalItems
      totalAmount
    }
  }
}
```

## Các tính năng đã implement:

### Queries:
- ✅ `myCart` - Lấy giỏ hàng của user hiện tại
- ✅ `cartItems` - Lấy danh sách items trong giỏ hàng

### Mutations:
- ✅ `addToCart` - Thêm sản phẩm vào giỏ hàng
  - Tự động tạo cart nếu chưa có
  - Kiểm tra stock trước khi thêm
  - Cộng dồn quantity nếu sản phẩm đã có trong cart
  - Cập nhật giá theo final_price hoặc price hiện tại

- ✅ `removeFromCart` - Xóa sản phẩm khỏi giỏ hàng
  - Xóa cart item theo ID
  - Kiểm tra quyền sở hữu (chỉ xóa được item của mình)

- ✅ `updateCartItemQuantity` - Cập nhật số lượng
  - Kiểm tra stock trước khi update
  - Cập nhật giá theo giá hiện tại
  - Validate quantity > 0

- ✅ `clearCart` - Xóa tất cả sản phẩm
  - Xóa toàn bộ items trong cart
  - Giữ lại cart object

## Validation & Error Handling:
- ✅ Kiểm tra authentication
- ✅ Kiểm tra stock availability
- ✅ Kiểm tra variant tồn tại và active
- ✅ Kiểm tra quantity hợp lệ
- ✅ Transaction atomic cho tất cả mutations
- ✅ Error messages tiếng Việt
