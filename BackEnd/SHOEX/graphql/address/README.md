# Address GraphQL API

GraphQL API implementation cho module Address, bao gồm quản lý Tỉnh/Thành phố, Phường/Xã, Thôn/Xóm và Địa chỉ người dùng.

## Cấu trúc

```
graphql_api/address/
├── __init__.py
├── schema.py                 # Schema chính
├── types/
│   ├── __init__.py
│   └── address.py           # GraphQL types cho tất cả models
├── mutations/
│   ├── __init__.py
│   └── address_mutations.py # CRUD mutations
├── filters/
│   ├── __init__.py
│   └── address_filters.py   # Filters cho queries
└── dataloaders/
    ├── __init__.py
    └── address_loaders.py   # DataLoaders để optimize N+1 queries
```

## Models được hỗ trợ

- **Province**: Tỉnh/Thành phố
- **Ward**: Phường/Xã
- **Hamlet**: Thôn/Xóm
- **Address**: Địa chỉ người dùng

## GraphQL Types

### ProvinceType

```graphql
type Province {
  provinceId: ID!
  name: String!
  totalWards: Int
  totalAddresses: Int
  wards: [Ward]
  addresses: [Address]
}
```

### WardType

```graphql
type Ward {
  wardId: ID!
  name: String!
  province: Province!
  totalHamlets: Int
  totalAddresses: Int
  fullName: String
  hamlets: [Hamlet]
  addresses: [Address]
}
```

### HamletType

```graphql
type Hamlet {
  hamletId: ID!
  name: String!
  ward: Ward!
  totalAddresses: Int
  fullName: String
  addresses: [Address]
}
```

### AddressType

```graphql
type Address {
  addressId: ID!
  user: User!
  province: Province!
  ward: Ward!
  hamlet: Hamlet
  detail: String!
  isDefault: Boolean!
  fullAddress: String
}
```

## Queries

### Single Queries

```graphql
# Lấy một tỉnh/thành
query GetProvince($id: ID!) {
  province(id: $id) {
    provinceId
    name
    totalWards
    wards {
      wardId
      name
    }
  }
}

# Lấy một địa chỉ
query GetAddress($id: ID!) {
  address(id: $id) {
    addressId
    detail
    fullAddress
    isDefault
    province {
      name
    }
    ward {
      name
    }
    hamlet {
      name
    }
  }
}
```

### List Queries với Filtering

```graphql
# Danh sách tỉnh/thành với filter
query GetProvinces($filter: ProvinceFilterInput, $first: Int, $after: String) {
  provinces(filter: $filter, first: $first, after: $after) {
    edges {
      node {
        provinceId
        name
        totalWards
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}

# Danh sách địa chỉ với filter
query GetAddresses($filter: AddressFilterInput, $first: Int, $after: String) {
  addresses(filter: $filter, first: $first, after: $after) {
    edges {
      node {
        addressId
        fullAddress
        isDefault
        user {
          username
        }
      }
    }
  }
}
```

### Custom Queries

```graphql
# Địa chỉ của user
query GetUserAddresses($userId: ID!) {
  userAddresses(userId: $userId) {
    addressId
    fullAddress
    isDefault
  }
}

# Địa chỉ mặc định của user
query GetUserDefaultAddress($userId: ID!) {
  userDefaultAddress(userId: $userId) {
    addressId
    fullAddress
  }
}

# Phường/xã trong tỉnh
query GetWardsByProvince($provinceId: ID!) {
  wardsByProvince(provinceId: $provinceId) {
    wardId
    name
  }
}

# Thôn/xóm trong phường
query GetHamletsByWard($wardId: ID!) {
  hamletsByWard(wardId: $wardId) {
    hamletId
    name
  }
}

# Tìm kiếm địa chỉ
query SearchAddresses($searchTerm: String!, $limit: Int) {
  searchAddresses(searchTerm: $searchTerm, limit: $limit) {
    addressId
    fullAddress
    user {
      username
    }
  }
}
```

## Mutations

### Province Mutations

```graphql
# Tạo tỉnh/thành mới
mutation CreateProvince($input: ProvinceInput!) {
  createProvince(input: $input) {
    province {
      provinceId
      name
    }
    errors {
      message
    }
  }
}

# Cập nhật tỉnh/thành
mutation UpdateProvince($id: ID!, $input: ProvinceInput!) {
  updateProvince(id: $id, input: $input) {
    province {
      provinceId
      name
    }
    errors {
      message
    }
  }
}

# Xóa tỉnh/thành
mutation DeleteProvince($id: ID!) {
  deleteProvince(id: $id) {
    success
    errors {
      message
    }
  }
}
```

### Address Mutations

```graphql
# Tạo địa chỉ mới
mutation CreateAddress($input: AddressInput!) {
  createAddress(input: $input) {
    address {
      addressId
      fullAddress
      isDefault
    }
    errors {
      message
    }
  }
}

# Cập nhật địa chỉ
mutation UpdateAddress($id: ID!, $input: AddressInput!) {
  updateAddress(id: $id, input: $input) {
    address {
      addressId
      fullAddress
    }
    errors {
      message
    }
  }
}

# Đặt làm địa chỉ mặc định
mutation SetDefaultAddress($id: ID!) {
  setDefaultAddress(id: $id) {
    address {
      addressId
      isDefault
    }
    errors {
      message
    }
  }
}

# Xóa địa chỉ
mutation DeleteAddress($id: ID!) {
  deleteAddress(id: $id) {
    success
    errors {
      message
    }
  }
}
```

## Filters

### ProvinceFilter

- `name_contains`: Tìm tỉnh có chứa từ khóa
- `name_exact`: Tìm tỉnh có tên chính xác
- `min_wards`: Tỉnh có ít nhất n phường/xã
- `max_wards`: Tỉnh có nhiều nhất n phường/xã

### WardFilter

- `name_contains`: Tìm phường/xã có chứa từ khóa
- `province_name`: Tìm theo tên tỉnh/thành
- `province_id`: Filter theo ID tỉnh/thành
- `min_hamlets`: Phường/xã có ít nhất n thôn/xóm
- `max_hamlets`: Phường/xã có nhiều nhất n thôn/xóm

### AddressFilter

- `user_id`: Filter theo ID người dùng
- `user_username`: Tìm theo username
- `detail_contains`: Tìm trong địa chỉ chi tiết
- `province_name`: Tìm theo tên tỉnh/thành
- `ward_name`: Tìm theo tên phường/xã
- `hamlet_name`: Tìm theo tên thôn/xóm
- `is_default`: Filter địa chỉ mặc định
- `search`: Tìm kiếm toàn văn

## Sử dụng

### 1. Import vào main schema

```python
# trong main schema.py
from graphql_api.address.schema import AddressQuery, AddressMutation

class Query(AddressQuery, ProductQuery, ...):
    pass

class Mutation(AddressMutation, ProductMutation, ...):
    pass
```

### 2. Cấu hình DataLoaders

```python
# trong GraphQL context
from graphql_api.address.dataloaders.address_loaders import AddressDataLoaders

def get_context(request):
    return {
        'request': request,
        'address_dataloaders': AddressDataLoaders(),
        # ... other dataloaders
    }
```

### 3. Example sử dụng trong frontend

```javascript
// React/Apollo Client example
const GET_USER_ADDRESSES = gql`
  query GetUserAddresses($userId: ID!) {
    userAddresses(userId: $userId) {
      addressId
      fullAddress
      isDefault
      province {
        name
      }
      ward {
        name
      }
    }
  }
`;

const CREATE_ADDRESS = gql`
  mutation CreateAddress($input: AddressInput!) {
    createAddress(input: $input) {
      address {
        addressId
        fullAddress
      }
      errors {
        message
      }
    }
  }
`;
```

## Performance

- **DataLoaders**: Sử dụng DataLoaders để giải quyết N+1 query problem
- **Select/Prefetch Related**: Optimize database queries
- **Pagination**: Hỗ trợ Relay-style pagination
- **Filtering**: Efficient filtering với django-filter

## Dependencies

- `graphene-django`
- `django-filter`
- `promise` (cho DataLoaders)

Đảm bảo cài đặt các dependencies này trong requirements.txt của project.
