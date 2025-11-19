# User GraphQL API Documentation

## Overview

This document provides the GraphQL API documentation for User management operations including authentication, user CRUD operations, and role management.

## Base URL

- GraphQL Endpoint: `http://localhost:8000/graphql/`
- GraphiQL Interface: `http://localhost:8000/graphql/` (for testing)

---

## Queries

### 1. Health Check

Kiểm tra trạng thái server

```graphql
query {
  health
}
```

### 2. Lấy danh sách users

Lấy thông tin tất cả users trong hệ thống

```graphql
query {
  users {
    id
    username
    email
    fullName
    role
  }
}
```

### 3. Lấy thông tin user hiện tại

Lấy thông tin user đang đăng nhập (cần token)

```graphql
query {
  me {
    id
    username
    email
    fullName
    role
  }
}
```

---

## Mutations

### 1. Tạo tài khoản

Đăng ký tài khoản mới (role mặc định là "buyer")

```graphql
mutation {
  register(
    input: {
      fullName: "Nguyen Van A"
      username: "nguyenvana"
      email: "nguyenvana@example.com"
      password: "matkhau123"
    }
  ) {
    success
    message
    user {
      id
      username
      email
      fullName
      role
    }
    errors {
      username
      email
      password
      general
    }
  }
}
```

### 2. Đăng nhập

Xác thực người dùng và nhận token

```graphql
mutation {
  login(input: { username: "nguyenvana", password: "matkhau123" }) {
    success
    message
    user {
      id
      username
      email
      fullName
      role
    }
    tokens {
      accessToken
      refreshToken
      expiresIn
    }
    errors {
      username
      password
      general
    }
  }
}
```

### 3. Đăng xuất

Hủy session của người dùng

```graphql
mutation {
  logout(input: {}) {
    success
    message
  }
}
```

### 4. Refresh Token

Gia hạn access token khi hết hạn bằng refresh token

```graphql
mutation {
  refreshToken(
    input: { refreshToken: "MQJWjpwE0N43djR3sHUO7bw-9GKPAuqPJ9yD2zjm4hY" }
  ) {
    success
    message
    tokens {
      accessToken
      refreshToken
      expiresIn
    }
    errors {
      general
    }
  }
}
```

### 5. Tạo user mới

Tạo user mới với quyền admin (cần xác thực)

```graphql
mutation {
  userCreate(
    input: {
      fullName: "Admin User"
      username: "adminuser"
      email: "admin@example.com"
      password: "adminpass123"
      role: "admin"
    }
  ) {
    success
    message
    user {
      id
      username
      email
      fullName
      role
    }
    errors {
      username
      email
      password
      role
      general
    }
  }
}
```

### 6. Cập nhật thông tin user

Chỉnh sửa thông tin user hiện có

```graphql
mutation {
  userUpdate(
    input: {
      userId: "1"
      fullName: "Nguyen Van B"
      email: "nguyenvanb@example.com"
    }
  ) {
    success
    message
    user {
      id
      username
      email
      fullName
      role
    }
    errors {
      userId
      email
      general
    }
  }
}
```

### 7. Xóa user

Xóa user khỏi hệ thống

```graphql
mutation {
  userDelete(input: { userId: "1" }) {
    success
    message
    errors {
      userId
      general
    }
  }
}
```

### 8. Đổi mật khẩu

Thay đổi mật khẩu user hiện tại

```graphql
mutation {
  passwordChange(
    input: { oldPassword: "matkhaucu123", newPassword: "matkhaumoi123" }
  ) {
    success
    message
    errors {
      oldPassword
      newPassword
      general
    }
  }
}
```

---

## Lưu ý

- Role mặc định khi tạo tài khoản: `"buyer"`
- Các role có sẵn: `"buyer"`, `"seller"`, `"admin"`
- Token JWT được trả về sau khi đăng nhập thành công
- Một số mutation cần quyền admin để thực hiện
