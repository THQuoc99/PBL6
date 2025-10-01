# Module User - GraphQL API

Module quản lý người dùng GraphQL toàn diện cho nền tảng thương mại điện tử SHOEX theo mẫu kiến trúc Django-Graphene với **Tích hợp Custom User Model**.

## 📁 Cấu trúc Module

````
graphql_api/user/
├── __init__.py                 # Xuất module
├── schema.py       ### Ví dụ Thay đổi (Mutations)

```graphql
# Tạo người dùng mới với các trường tùy chỉnh
mutation CreateUser {
  userCreate(
    input: {
      username: "testuser"
      email: "test@example.com"
      password: "SecurePassword123!"
      firstName: "Test"
      lastName: "User"
      fullName: "Test User Full Name"    # Trường tùy chỉnh
      phone: "0123456789"                # Trường tùy chỉnh
      role: "buyer"                      # Trường tùy chỉnh (đã xác thực)
      isActive: truehema GraphQL chính
├── README.md                   # Tài liệu này
├── types/
│   ├── __init__.py
│   └── user.py                 # Các kiểu GraphQL (UserType, GroupType, v.v.)
├── mutations/
│   ├── __init__.py
│   └── user_mutations.py       # Mutations CRUD
├── filters/
│   ├── __init__.py
│   └── user_filters.py         # Lọc và sắp xếp
├── dataloaders/
│   ├── __init__.py
│   └── user_loaders.py         # Tối ưu hóa truy vấn N+1
└── bulk_mutations/
    ├── __init__.py
    └── user_bulk_mutations.py   # Thao tác hàng loạt
````

## 🎯 Custom User Model Integration

This module integrates with SHOEX's custom User model (`users/models.py`):

```python
class User(AbstractUser):
    ROLE_CHOICES = [
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
        ('admin', 'Admin'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
```

### Các trường tùy chỉnh có sẵn trong GraphQL:

- `role`: Vai trò người dùng với các lựa chọn (buyer, seller, admin)
- `fullName`: Tên đầy đủ của người dùng
- `phone`: Số điện thoại liên hệ
- `createdAt`: Thời gian tạo tài khoản
- `roleDisplay`: Tên vai trò dễ đọc
- `isSeller`: Tính toán dựa trên vai trò
- `isCustomer`: Tính toán dựa trên vai trò (buyer)

## 🚀 Tính năng

### Kiểu GraphQL

- **UserType**: Thông tin người dùng đầy đủ với tích hợp profile
- **GroupType**: Quản lý nhóm Django
- **UserProfileType**: Dữ liệu profile người dùng mở rộng
- **UserConnection/GroupConnection**: Hỗ trợ phân trang

### Truy vấn (Queries)

```graphql
# Người dùng đơn lẻ
user(id: ID!): UserType
group(id: ID!): GroupType
me: UserType  # Người dùng hiện tại đã xác thực

# Danh sách với lọc và phân trang
users(filter: UserFilterInput, sortBy: String, search: String): UserConnection
groups(filter: GroupFilterInput, sortBy: String, search: String): GroupConnection

# Truy vấn chuyên biệt
activeUsers: UserConnection
staffUsers: UserConnection
usersByGroup(groupId: ID!): UserConnection

# Thống kê
userCount: Int
activeUserCount: Int
staffUserCount: Int
groupCount: Int

# Hồ sơ
userProfile(userId: ID): UserProfileType
```

### Thay đổi (Mutations)

```graphql
# Quản lý người dùng
userCreate(input: UserCreateInput!): UserCreate
userUpdate(input: UserUpdateInput!): UserUpdate
userDelete(id: ID!): UserDelete
passwordChange(oldPassword: String!, newPassword: String!): PasswordChange

# Quản lý nhóm
groupCreate(name: String!, permissions: [ID!]): GroupCreate
groupUpdate(id: ID!, name: String, permissions: [ID!]): GroupUpdate
groupDelete(id: ID!): GroupDelete

# Mối quan hệ Người dùng-Nhóm
userGroupAdd(userId: ID!, groupId: ID!): UserGroupAdd
userGroupRemove(userId: ID!, groupId: ID!): UserGroupRemove

# Thao tác hàng loạt
bulkUserCreate(usersData: [BulkUserCreateInput!]!): BulkUserCreate
bulkUserUpdate(usersData: [BulkUserUpdateInput!]!): BulkUserUpdate
bulkUserDelete(userIds: [ID!]!, hardDelete: Boolean): BulkUserDelete
bulkUserActivate(userIds: [ID!]!, isActive: Boolean!): BulkUserActivate
```

### Lọc & Sắp xếp

```graphql
input UserFilterInput {
  # Lọc theo văn bản
  username: String
  usernameIcontains: String
  email: String
  emailIcontains: String
  firstNameIcontains: String
  lastNameIcontains: String

  # Lọc theo trường tùy chỉnh
  fullNameIcontains: String
  phoneIcontains: String
  role: String # "buyer", "seller", "admin"
  # Boolean filters
  isActive: Boolean
  isStaff: Boolean
  isSuperuser: Boolean

  # Date filters
  dateJoinedGte: DateTime
  dateJoinedLte: DateTime
  lastLoginGte: DateTime
  lastLoginLte: DateTime

  # Relationship filters
  groups: [ID!]
  hasProducts: Boolean

  # Search across multiple fields (includes custom fields)
  search: String
}
```

### DataLoaders (Tối ưu hóa N+1)

- `UserLoader`: Tải người dùng theo batch theo ID
- `UserByUsernameLoader`: Tải người dùng theo username
- `UserByEmailLoader`: Tải người dùng theo email
- `GroupLoader`: Tải nhóm theo batch
- `UserGroupsLoader`: Tải các nhóm của người dùng
- `GroupUsersLoader`: Tải các người dùng của nhóm
- `UserProductCountLoader`: Tải số lượng sản phẩm của người dùng
- `UserPermissionsLoader`: Tải quyền của người dùng
- `UserStatsLoader`: Tải thống kê toàn diện của người dùng

## 🔧 Tích hợp

### 1. Thêm vào Schema GraphQL chính

Trong `graphql_api/api.py`:

```python
from .user.schema import UserQuery, UserMutation

class Query(
    ProductQueries,
    UserQuery,
    graphene.ObjectType
):
    pass

class Mutation(
    ProductMutations,
    UserMutation,
    graphene.ObjectType
):
    pass
```

### 2. Thiết lập Context DataLoader

Trong Django middleware hoặc GraphQL view:

```python
from graphql_api.user.dataloaders.user_loaders import create_user_loaders

class GraphQLContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Thêm user loaders vào request context
        request.user_loaders = create_user_loaders()
        response = self.get_response(request)
        return response
```

## 📝 Ví dụ sử dụng

### Ví dụ Truy vấn

````graphql
```graphql
# Lấy người dùng hiện tại với các trường tùy chỉnh
query Me {
  me {
    id
    username
    email
    firstName
    lastName
    fullName          # Trường tùy chỉnh
    phone             # Trường tùy chỉnh
    role              # Trường tùy chỉnh
    roleDisplay       # Trường hỗ trợ
    displayName       # Trường tính toán ưu tiên fullName
    initials          # Trường tính toán sử dụng fullName
    createdAt         # Trường tùy chỉnh
    dateJoined
    isActive
    isSeller          # Dựa trên vai trò
    isCustomer        # Dựa trên vai trò (buyer)

# Tìm kiếm người dùng với lọc trường tùy chỉnh
query SearchUsers {
  users(
    filter: {
      role: "seller"
      fullNameIcontains: "Nguyen"
      phoneIcontains: "0123"
      isActive: true
    }
    sortBy: "DATE_JOINED_DESC"
    first: 10
  ) {
    edges {
      node {
        id
        username
        email
        fullName
        phone
        role
        roleDisplay
        isSeller
        productCount
        createdAt
      }
    }
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
    }
  }
}

# Filter by role
query GetSellerUsers {
  users(filter: { role: "seller", isActive: true }, sortBy: "CREATED_AT_DESC") {
    edges {
      node {
        id
        username
        fullName
        phone
        role
        createdAt
        isSeller
      }
    }
  }
}

# Get user statistics
query UserStats {
  userCount
  activeUserCount
  staffUserCount
  groupCount
}
````

### Mutation Examples

```graphql
# Create new user with custom fields
mutation CreateUser {
  userCreate(
    input: {
      username: "testuser"
      email: "test@example.com"
      password: "SecurePassword123!"
      firstName: "Test"
      lastName: "User"
      fullName: "Test User Full Name" # Custom field
      phone: "0123456789" # Custom field
      role: "buyer" # Custom field (validated)
      isActive: true
    }
  ) {
    user {
      id
      username
      email
      fullName
      phone
      role
      roleDisplay
      displayName
      isSeller
    }
    success
    message
  }
}

# Cập nhật người dùng với các trường tùy chỉnh
mutation UpdateUser($id: ID!)	 {
  userUpdate(
    id: $id
    input: {
      fullName: "Updated Full Name"
      phone: "0987654321"
      role: "seller"
    }
  ) {
    user {
      id
      fullName
      phone
      role
      roleDisplay
      isSeller
    }
    success
    message
  }
}

# Tạo hàng loạt người dùng với các trường tùy chỉnh
mutation BulkCreateUsers {
  bulkUserCreate(
    usersData: [
      {
        username: "buyer1"
        email: "buyer1@example.com"
        password: "Password123!"
        fullName: "Buyer User One"
        phone: "0111111111"
        role: "buyer"
      }
      {
        username: "seller1"
        email: "seller1@example.com"
        password: "Password123!"
        fullName: "Seller User One"
        phone: "0222222222"
        role: "seller"
      }
    ]
  ) {
    result {
      users {
        id
        username
        fullName
        role
        roleDisplay
      }
      success
      message
      createdCount
      failedCount
      errors
    }
  }
}
```

## 🔒 Xác thực & Quyền

- Tất cả mutations yêu cầu xác thực (`user.is_authenticated`)
- Các thao tác quản trị yêu cầu quyền nhân viên (`user.is_staff`)
- Người dùng chỉ có thể sửa đổi dữ liệu của chính mình (trừ admin)
- Các thao tác superuser yêu cầu trạng thái superuser
- Quản lý nhóm yêu cầu đặc quyền nhân viên

## 🎯 Thực hành tốt nhất

1. **Sử dụng DataLoaders**: Luôn truy cập dữ liệu liên quan thông qua DataLoaders để tránh truy vấn N+1
2. **Lọc ở cấp Database**: Sử dụng bộ lọc GraphQL thay vì lọc Python để tăng hiệu suất
3. **Phân trang**: Luôn sử dụng kiểu Connection cho các danh sách có thể phát triển lớn
4. **Xác thực Input**: Tận dụng các validators có sẵn của Django trong mutations
5. **An toàn giao dịch**: Sử dụng database transactions cho các thao tác nhiều bước
6. **Xử lý lỗi**: Cung cấp thông báo lỗi có ý nghĩa cho người dùng

## 🔗 Các Module liên quan

- **Product Module**: Mối quan hệ người dùng-sản phẩm và quyền sở hữu
- **Order Module**: Lịch sử đơn hàng và quản lý của người dùng
- **Review Module**: Đánh giá và xếp hạng của người dùng
- **Authentication**: Tích hợp hệ thống xác thực có sẵn của Django

## 📊 Cân nhắc về hiệu suất

- DataLoaders giảm truy vấn cơ sở dữ liệu từ O(n) xuống O(1)
- Index cơ sở dữ liệu trên username, email và các trường thường lọc
- Phân trang dựa trên Connection ngăn chặn vấn đề bộ nhớ với dataset lớn
- Tối ưu hóa querysets với select_related() và prefetch_related()

## 🧪 Kiểm thử & Xác thực

### Testing Steps

1. **Setup Database**:

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
2. **Create Test Users**:

   ```python
   from users.models import User

   # Create buyer
   buyer = User.objects.create_user(
       username='buyer_test',
       email='buyer@test.com',
       password='testpass123',
       full_name='Test Buyer',
       phone='0123456789',
       role='buyer'
   )

   # Create seller
   seller = User.objects.create_user(
       username='seller_test',
       email='seller@test.com',
       password='testpass123',
       full_name='Test Seller',
       phone='0987654321',
       role='seller'
   )
   ```
3. **Test GraphQL Endpoint**:

   - Navigate to `/graphql/` in browser (GraphiQL interface)
   - Run the queries above
   - Verify custom fields are returned correctly

### Kết quả mong đợi

- ✅ Các trường tùy chỉnh (role, full_name, phone, created_at) nên có thể truy cập được
- ✅ Các trường tính toán dựa trên vai trò (is_seller, is_customer) nên hoạt động
- ✅ Lọc theo các trường tùy chỉnh nên hoạt động
- ✅ Tên hiển thị nên ưu tiên full_name hơn first_name + last_name
- ✅ Xác thực vai trò nên ngăn chặn các giá trị vai trò không hợp lệ
- ✅ Các thao tác hàng loạt nên xử lý các trường tùy chỉnh đúng cách

### Danh sách kiểm tra tích hợp

- [X] UserType đã cập nhật với các trường tùy chỉnh
- [X] Các kiểu input đã cập nhật cho các trường tùy chỉnh
- [X] Mutations xử lý xác thực trường tùy chỉnh
- [X] Bộ lọc bao gồm lọc trường tùy chỉnh
- [X] Tìm kiếm bao gồm các trường tùy chỉnh
- [X] Các thao tác hàng loạt hỗ trợ các trường tùy chỉnh
- [X] Xác thực vai trò đã được triển khai
- [X] Các trường tính toán sử dụng các trường tùy chỉnh khi có sẵn
- [X] Tài liệu đã được cập nhật

### Bảo hiểm kiểm thử

Module bao gồm bảo hiểm kiểm thử toàn diện cho:

- Sửa đổi kiểu GraphQL với các trường tùy chỉnh
- Xác thực mutation và logic kinh doanh
- Lọc và xác thực dựa trên vai trò
- Chức năng tìm kiếm trường tùy chỉnh
- Hiệu suất DataLoader với các trường tùy chỉnh
- Kiểm tra quyền và xác thực
- Tính nguyên tử thao tác hàng loạt với các trường tùy chỉnh

---

**Được tạo cho Nền tảng Thương mại Điện tử SHOEX**
_Tích hợp Custom User Model Hoàn thành_ ✅
_Theo mẫu kiến trúc Saleor/Django-Graphene_
