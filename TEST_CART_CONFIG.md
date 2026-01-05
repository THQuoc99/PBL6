# Kiểm tra cấu hình Cart API

## 1. Backend Configuration ✅

### JWT Middleware
- ✅ File: `config/jwt_middleware.py` đã tồn tại
- ✅ Đã thêm vào MIDDLEWARE trong `settings.py`
- ✅ Middleware extract user từ JWT token trong Authorization header

### Django Settings
```python
# MIDDLEWARE - Đã thêm JWT
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'config.jwt_middleware.JWTAuthenticationMiddleware',  # ← JWT Auth
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# CORS - Hỗ trợ localhost:3000
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Session - Hỗ trợ cross-domain
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_DOMAIN = None  # Hỗ trợ cả localhost và 127.0.0.1
SESSION_SAVE_EVERY_REQUEST = True
```

### Cart Mutations - Sử dụng info.context.user
```python
# AddToCart
user = info.context.user
if not user or not user.is_authenticated:
    return AddToCart(success=False, errors=["Vui lòng đăng nhập"])

cart, created = Cart.objects.get_or_create(
    user=user,
    session_key=None
)

# RemoveFromCart
user = info.context.user
cart_item = CartItem.objects.get(
    item_id=item_id,
    cart__user=user
)

# UpdateCartItemQuantity
user = info.context.user
cart_item = CartItem.objects.get(
    item_id=item_id,
    cart__user=user
)

# ClearCart
user = info.context.user
cart = Cart.objects.get(user=user)
```

### Cart Query - my_cart
```python
def resolve_my_cart(self, info):
    user = info.context.user
    if not user or not user.is_authenticated:
        return None
    
    cart = Cart.objects.get(user=user)
    return cart
```

## 2. Frontend Configuration ✅

### API URL
- ✅ Đã đổi từ `localhost:8000` → `127.0.0.1:8000`
- ✅ Match với backend đang chạy

### Auth Service - credentials: 'include'
```typescript
// apiCall method
const response = await fetch(this.API_URL, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${accessToken}`,
  },
  credentials: 'include', // ← Gửi/nhận cookies
  body: JSON.stringify({ query, variables }),
});

// Retry fetch
const retryResponse = await fetch(this.API_URL, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${newAccessToken}`,
  },
  credentials: 'include', // ← Gửi/nhận cookies
  body: JSON.stringify({ query, variables }),
});
```

### Cart Service
- ✅ Sử dụng `authService.apiCall()` để gọi API
- ✅ Token được tự động thêm vào header
- ✅ User authentication được check ở backend

## 3. Flow hoạt động

### Khi user thêm sản phẩm vào giỏ hàng:

1. **Frontend (ProductDetailPage)**
   ```typescript
   const handleAddToCart = async () => {
     if (!isAuthenticated) {
       alert('Vui lòng đăng nhập');
       return;
     }
     
     const result = await addToCart(selectedVariantId, quantity);
   }
   ```

2. **Cart Service**
   ```typescript
   const result = await authService.apiCall(query, { variantId, quantity });
   ```

3. **Auth Service**
   - Lấy token từ localStorage
   - Gửi request với header: `Authorization: Bearer <token>`
   - Gửi kèm `credentials: 'include'` để gửi cookies

4. **Backend - Django Middleware**
   - CORS middleware: Check origin, cho phép localhost:3000
   - Session middleware: Tạo/lấy session
   - Auth middleware: Authenticate user từ database
   - **JWT middleware**: Extract token → Get user → Set `request.user`

5. **Backend - GraphQL Resolver**
   ```python
   user = info.context.user  # ← User từ JWT
   if not user or not user.is_authenticated:
       return error
   
   cart = Cart.objects.get_or_create(user=user)
   ```

6. **Response về Frontend**
   ```json
   {
     "data": {
       "addToCart": {
         "success": true,
         "cartItem": { ... }
       }
     }
   }
   ```

## 4. Kiểm tra từng bước

### Bước 1: Kiểm tra Backend đang chạy
```bash
# Terminal 1
cd d:\PBL6\BackEnd\SHOEX
python manage.py runserver 127.0.0.1:8000
```

Kết quả mong muốn:
```
Starting development server at http://127.0.0.1:8000/
```

### Bước 2: Kiểm tra Frontend đang chạy
```bash
# Terminal 2
cd "d:\PBL6\FE_web copy"
npm run dev
```

Kết quả mong muốn:
```
ready - started server on 0.0.0.0:3000, url: http://localhost:3000
```

### Bước 3: Test Authentication
1. Mở browser: http://localhost:3000
2. Đăng nhập
3. Mở DevTools → Console
4. Chạy:
   ```javascript
   localStorage.getItem('accessToken')
   ```
   Phải có token

### Bước 4: Test Cart API
1. Vào trang sản phẩm: http://localhost:3000/product/2
2. Chọn size, color
3. Click "Thêm vào giỏ hàng"
4. Mở DevTools → Network → GraphQL request
5. Check:
   - Request Headers: `Authorization: Bearer <token>`
   - Request Headers: `Cookie: sessionid=...`
   - Response: `success: true`

### Bước 5: Test Backend nhận được User
Thêm debug log vào `mutations.py`:
```python
def mutate_and_get_payload(cls, root, info, **input):
    user = info.context.user
    print(f"🔍 User: {user}")
    print(f"🔍 Is authenticated: {user.is_authenticated if user else False}")
    print(f"🔍 User ID: {user.id if user and user.is_authenticated else 'None'}")
```

## 5. Troubleshooting

### Lỗi: "Vui lòng đăng nhập"
**Nguyên nhân**: Backend không nhận được user từ JWT

**Kiểm tra**:
1. Token có trong localStorage không?
   ```javascript
   localStorage.getItem('accessToken')
   ```

2. Token có được gửi trong header không?
   - DevTools → Network → Request Headers
   - Phải thấy: `Authorization: Bearer eyJ...`

3. JWT middleware có được load không?
   - Check `settings.py` → MIDDLEWARE
   - Phải có: `'config.jwt_middleware.JWTAuthenticationMiddleware'`

4. Token có hợp lệ không?
   - Đăng xuất và đăng nhập lại
   - Check token mới

### Lỗi: CORS
**Triệu chứng**: Console error "CORS policy"

**Giải pháp**:
```python
# settings.py
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
```

### Lỗi: Session cookies
**Triệu chứng**: Cookies không được gửi

**Giải pháp**:
```typescript
// auth.ts
credentials: 'include'
```

```python
# settings.py
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_DOMAIN = None
```

## 6. Checklist

Backend:
- [x] JWT middleware trong settings.py
- [x] CORS_ALLOW_CREDENTIALS = True
- [x] SESSION_COOKIE_DOMAIN = None
- [x] Cart mutations dùng info.context.user
- [x] my_cart query dùng info.context.user

Frontend:
- [x] API_URL = 'http://127.0.0.1:8000/graphql/'
- [x] credentials: 'include' trong fetch
- [x] Authorization header với Bearer token
- [x] Cart service dùng authService.apiCall

## 7. Test Commands

### Backend logs
```bash
cd d:\PBL6\BackEnd\SHOEX
python manage.py runserver 127.0.0.1:8000
# Watch terminal for print statements
```

### Frontend console
```javascript
// Check token
localStorage.getItem('accessToken')

// Check user
authService.getCurrentUser()

// Test add to cart
cartService.addToCart('variant-id', 1)
```
