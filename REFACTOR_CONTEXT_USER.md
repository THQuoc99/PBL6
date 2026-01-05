# Cập nhật: Sử dụng info.context.user và API Client

## ✅ Các thay đổi đã thực hiện:

### 1. Backend - JWT Middleware (FIXED)

**File**: `config/jwt_middleware.py`

- ✅ Trả về `AnonymousUser()` thay vì `None`
- ✅ Chỉ xử lý requests có `Authorization` header (không can thiệp Django Admin)
- ✅ Django Admin giờ hoạt động bình thường

```python
def get_user_from_token(request):
    # Returns AnonymousUser() instead of None
    if not auth_header.startswith('Bearer '):
        return AnonymousUser()
    # ...
    except:
        return AnonymousUser()

class JWTAuthenticationMiddleware:
    def __call__(self, request):
        # Chỉ override user nếu có Authorization header
        if 'HTTP_AUTHORIZATION' in request.META:
            request.user = SimpleLazyObject(lambda: get_user_from_token(request))
```

### 2. Backend - Store Schema

**File**: `graphql_api/store/schema.py`

**Query `myOwnedStore` - Không cần userId**

```python
# TRƯỚC:
my_owned_store = graphene.Field(
    StoreType,
    user_id=ID(required=False),  # ❌ Cần truyền userId
)

def resolve_my_owned_store(self, info, user_id=None):
    if user_id is None:
        target_user = info.context.user
    else:
        target_user = User.objects.get(id=user_id)

# SAU:
my_owned_store = graphene.Field(
    StoreType,
    description="Lấy cửa hàng duy nhất mà user đang đăng nhập là owner"
)

def resolve_my_owned_store(self, info):
    user = info.context.user  # ✅ Tự động lấy từ JWT
    if not user or not user.is_authenticated:
        return None
  
    membership = StoreUser.objects.filter(
        user=user,
        role='owner',
        status='active'
    ).select_related('store').first()
  
    return membership.store if membership else None
```

### 3. Backend - User Schema

**File**: `graphql_api/user/schema.py`

**Query `userProfile` - Không cần userId**

```python
# TRƯỚC:
user_profile = Field(UserProfileType, user_id=ID())

def resolve_user_profile(self, info, user_id=None):
    if user_id:
        user = User.objects.get(id=user_id)
    else:
        user = info.context.user

# SAU:
user_profile = Field(
    UserProfileType, 
    description="Lấy user profile của user đang đăng nhập"
)

def resolve_user_profile(self, info):
    user = info.context.user  # ✅ Tự động lấy từ JWT
    if not user or not user.is_authenticated:
        return None
    return UserProfileType(user=user)
```

### 4. Frontend - API Client (MỚI)

**File**: `services/apiClient.ts`

Tách logic API calls thành file riêng:

```typescript
export class ApiClient {
  private readonly API_URL = 'http://127.0.0.1:8000/graphql/';

  // Public API (không cần token)
  async publicApiCall(query: string, variables?: any): Promise<ApiResponse>

  // Authenticated API (tự động thêm token + refresh khi hết hạn)
  async authenticatedApiCall(query: string, variables?: any): Promise<ApiResponse>
  
  private async refreshToken(): Promise<boolean>
  private isTokenExpired(token: string): boolean
  private clearTokens(): void
}

export const apiClient = ApiClient.getInstance();
```

### 5. Frontend - Auth Service

**File**: `services/auth.ts`

- ✅ Import `apiClient`
- ✅ Delegate API calls tới apiClient:

```typescript
import { apiClient } from './apiClient';

// Gọi API không cần xác thực
async publicApiCall(query: string, variables?: any): Promise<ApiResponse> {
  return apiClient.publicApiCall(query, variables);
}

// Gọi API với authentication tự động
async apiCall(query: string, variables?: any): Promise<ApiResponse> {
  return apiClient.authenticatedApiCall(query, variables);
}
```

- ✅ `getUserProfile()` không cần userId:

```typescript
// TRƯỚC:
async getUserProfile(userId?: string)

const query = `
  query {
    userProfile${finalUserId ? `(userId: "${finalUserId}")` : ''} {
      user { ... }
    }
  }
`;

// SAU:
async getUserProfile()  // ❌ Không cần userId

const query = `
  query {
    userProfile {  // ✅ Tự động lấy từ context.user
      user { ... }
    }
  }
`;
```

### 6. Frontend - Store Service

**File**: `services/store.ts`

- ✅ Import `apiClient` thay vì `AuthService`
- ✅ `loadMyOwnedStore()` không cần userId:

```typescript
// TRƯỚC:
import { AuthService } from './auth';
const authService = AuthService.getInstance();

async loadMyOwnedStore(userId?: string): Promise<any | null> {
  const query = `
    query  {
      myOwnedStore(userId: ${userId}) { ... }
    }
  `;
  const result = await authService.apiCall(query, variables);
}

// SAU:
import { apiClient } from './apiClient';

async loadMyOwnedStore(): Promise<any | null> {
  const query = `
    query  {
      myOwnedStore { ... }  // ✅ Không cần userId
    }
  `;
  const result = await apiClient.authenticatedApiCall(query);
}
```

- ✅ Tất cả methods dùng `apiClient`:
  - `createStore()` → `apiClient.authenticatedApiCall()`
  - `getStore()` → `apiClient.authenticatedApiCall()`
  - `updateStore()` → `apiClient.authenticatedApiCall()`
  - `getAddressStores()` → `apiClient.authenticatedApiCall()`
  - `getStoreMembers()` → `apiClient.authenticatedApiCall()`
  - `addStoreMember()` → `apiClient.authenticatedApiCall()`

## 📋 API Usage Examples

### Frontend - Lấy User Profile

```typescript
// ✅ Không cần userId
const profile = await authService.getUserProfile();
```

### Frontend - Lấy Store của User

```typescript
// ✅ Không cần userId
const store = await storeService.getCurrentStore();
```

### Frontend - Gọi API trực tiếp

```typescript
// Public API
const result = await apiClient.publicApiCall(`
  query {
    products { name price }
  }
`);

// Authenticated API (tự động thêm token)
const result = await apiClient.authenticatedApiCall(`
  query {
    myCart { totalItems }
  }
`);
```

## 🔒 Security Flow

1. **User đăng nhập** → Nhận JWT token → Lưu localStorage
2. **Frontend gọi API** → `apiClient.authenticatedApiCall()`
3. **ApiClient** → Thêm `Authorization: Bearer <token>` vào header
4. **Django Middleware** → JWT Middleware extract token
5. **JWT Middleware** → `request.user = User or AnonymousUser`
6. **GraphQL Resolver** → `user = info.context.user`
7. **Business Logic** → Check `user.is_authenticated`

## ✅ Benefits

1. **Không cần truyền userId** - Tự động lấy từ JWT token
2. **Bảo mật hơn** - User không thể lấy data của người khác
3. **Code sạch hơn** - Ít parameters, queries ngắn gọn
4. **Tái sử dụng** - `apiClient` dùng chung cho tất cả services
5. **Django Admin hoạt động** - Middleware không can thiệp session auth

## 🧪 Test

### 1. Test Django Admin

```
http://127.0.0.1:8000/admin/
```

- ✅ Không còn lỗi `'NoneType' object has no attribute 'is_active'`

### 2. Test Store API

```javascript
// Console
const store = await storeService.getCurrentStore();
console.log(store.name);
```

### 3. Test User Profile

```javascript
const profile = await authService.getUserProfile();
console.log(profile.user.email);
```

## 📁 Files Changed

Backend:

- ✅ `config/jwt_middleware.py`
- ✅ `graphql_api/store/schema.py`
- ✅ `graphql_api/user/schema.py`

Frontend:

- ✅ `services/apiClient.ts` (NEW)
- ✅ `services/auth.ts`
- ✅ `services/store.ts`
