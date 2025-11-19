# GraphQL API Documentation - User Management

## 🚀 **Authentication & User Management APIs**

### **Base URL**

```
POST http://localhost:8000/graphql/
```

### **Headers**

```json
{
  "Content-Type": "application/json",
  "Authorization": "Bearer <your-jwt-token>" // Cho authenticated requests
}
```

---

## 📝 **1. ĐĂNG KÝ (REGISTER)**

### **Mutation**

```graphql
mutation {
  register(
    input: {
      fullName: "Nguyễn Văn A"
      username: "nguyenvana"
      email: "nguyenvana@gmail.com"
      password: "password123"
      birthDate: "1990-05-15"
    }
  ) {
    success
    message
    user {
      id
      username
      email
      fullName
      birthDate
      age
      role
      isActive
      dateJoined
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

### **cURL Test**

```bash
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation { register(input: { fullName: \"Nguyễn Văn A\", username: \"nguyenvana\", email: \"nguyenvana@gmail.com\", password: \"password123\", birthDate: \"1990-05-15\" }) { success message user { id username email fullName birthDate age role } errors { username email password general } } }"
  }'
```

### **Response**

```json
{
  "data": {
    "register": {
      "success": true,
      "message": "Đăng ký thành công",
      "user": {
        "id": "1",
        "username": "nguyenvana",
        "email": "nguyenvana@gmail.com",
        "fullName": "Nguyễn Văn A",
        "birthDate": "1990-05-15",
        "age": 35,
        "role": "buyer",
        "isActive": true,
        "dateJoined": "2025-11-19T10:30:00Z"
      },
      "errors": null
    }
  }
}
```

---

## 🔑 **2. ĐĂNG NHẬP (LOGIN)**

### **Mutation**

```graphql
mutation {
  login(
    input: { username: "nguyenvana", password: "password123", rememberMe: true }
  ) {
    success
    message
    user {
      id
      username
      email
      fullName
      firstName
      lastName
      phone
      birthDate
      age
      role
      avatarUrl
      isActive
      dateJoined
      lastLogin
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

### **cURL Test**

```bash
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation { login(input: { username: \"nguyenvana\", password: \"password123\", rememberMe: true }) { success message user { id username email fullName firstName lastName phone birthDate age role avatarUrl } tokens { accessToken refreshToken expiresIn } errors { username password general } } }"
  }'
```

### **Response**

```json
{
  "data": {
    "login": {
      "success": true,
      "message": "Đăng nhập thành công",
      "user": {
        "id": "1",
        "username": "nguyenvana",
        "email": "nguyenvana@gmail.com",
        "fullName": "Nguyễn Văn A",
        "firstName": "Văn",
        "lastName": "A",
        "phone": null,
        "birthDate": "1990-05-15",
        "age": 35,
        "role": "buyer",
        "avatarUrl": null,
        "isActive": true,
        "dateJoined": "2025-11-19T10:30:00Z",
        "lastLogin": "2025-11-19T11:00:00Z"
      },
      "tokens": {
        "accessToken": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "refreshToken": "abc123def456...",
        "expiresIn": 86400
      },
      "errors": null
    }
  }
}
```

---

## 🔄 **3. REFRESH TOKEN**

### **Mutation**

```graphql
mutation {
  refreshToken(input: { refreshToken: "abc123def456..." }) {
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

### **cURL Test**

```bash
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation { refreshToken(input: { refreshToken: \"abc123def456...\" }) { success tokens { accessToken refreshToken expiresIn } errors { general } } }"
  }'
```

---

## 🚪 **4. ĐĂNG XUẤT (LOGOUT)**

### **Mutation**

```graphql
mutation {
  logout(input: { refreshToken: "abc123def456..." }) {
    success
    message
  }
}
```

### **cURL Test**

```bash
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -d '{
    "query": "mutation { logout(input: { refreshToken: \"abc123def456...\" }) { success message } }"
  }'
```

---

## 👤 **5. LẤY THÔNG TIN USER HIỆN TẠI**

### **Query**

```graphql
query {
  userProfile {
    user {
      id
      username
      email
      fullName
      firstName
      lastName
      phone
      birthDate
      age
      role
      avatarUrl
      isActive
      dateJoined
      lastLogin
    }
  }
}
```

### **cURL Test**

```bash
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -d '{
    "query": "query { userProfile { user { id username email fullName firstName lastName phone birthDate age role avatarUrl isActive dateJoined lastLogin } } }"
  }'
```

---

## ✏️ **6. CẬP NHẬT THÔNG TIN USER**

### **Mutation**

```graphql
mutation {
  userUpdate(
    id: "3"
    input: {
      fullName: "Nguyễn Văn B"
      phone: "0123456789"
      email: "nguyenvanb@gmail.com"
      birthDate: "1992-03-20"
    }
  ) {
    success
    user {
      id
      username
      email
      fullName
      firstName
      lastName
      phone
      birthDate
      age
      role
      avatarUrl
      isActive
      dateJoined
      lastLogin
    }
    errors
  }
}
```

### **cURL Test**

```bash
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -d '{
    "query": "mutation { userUpdate(id: \"1\", input: { fullName: \"Nguyễn Văn B\", phone: \"0123456789\", birthDate: \"1992-03-20\" }) { success message user { fullName phone birthDate age } errors { phone general } } }"
  }'
```

---

## 📸 **7. UPLOAD AVATAR**

### **Mutation**

```graphql
mutation ($input: AvatarUploadInput!) {
  avatarUpload(input: $input) {
    success
    message
    avatarUrl
    user {
      id
      username
      avatarUrl
    }
  }
}
```

### **Variables**

```json
{
  "input": {
    "avatar": null
  }
}
```

### **cURL Test (Multipart)**

```bash
curl -X POST http://localhost:8000/graphql/ \
  -H "Authorization: Bearer <your-jwt-token>" \
  -F 'operations={"query":"mutation($input: AvatarUploadInput!) { avatarUpload(input: $input) { success message avatarUrl } }","variables":{"input":{"avatar":null}}}' \
  -F 'map={"0":["variables.input.avatar"]}' \
  -F '0=@avatar.jpg'
```

---

## 🗑️ **8. XÓA AVATAR**

### **Mutation**

```graphql
mutation {
  avatarDelete {
    success
    message
    user {
      id
      username
      email
      fullName
      firstName
      lastName
      phone
      birthDate
      age
      role
      avatarUrl
      isActive
      dateJoined
      lastLogin
    }
  }
}
```

### **cURL Test**

```bash
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -d '{
    "query": "mutation { avatarDelete { success message user { avatarUrl birthDate age } } }"
  }'
```

---

## 🔒 **9. ĐỔI MẬT KHẨU**

### **Mutation**

```graphql
mutation {
  passwordChange(
    input: { oldPassword: "password123", newPassword: "newpassword456" }
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

### **cURL Test**

```bash
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -d '{
    "query": "mutation { passwordChange(input: { oldPassword: \"password123\", newPassword: \"newpassword456\" }) { success message errors { oldPassword newPassword general } } }"
  }'
```

---

## 👥 **10. DANH SÁCH USER (ADMIN)**

### **Query**

```graphql
query {
  users(
    filter: { search: "nguyen", role: "buyer", isActive: true }
    sort: "dateJoined"
    pagination: { page: 1, pageSize: 10 }
  ) {
    users {
      id
      username
      email
      fullName
      birthDate
      age
      role
      isActive
      dateJoined
      lastLogin
      avatarUrl
    }
    totalCount
    pageInfo {
      currentPage
      totalPages
      hasNextPage
      hasPreviousPage
    }
  }
}
```

### **cURL Test**

```bash
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <admin-jwt-token>" \
  -d '{
    "query": "query { users(filter: { role: \"buyer\" }, pagination: { page: 1, pageSize: 10 }) { users { id username email fullName birthDate age role } totalCount pageInfo { currentPage totalPages } } }"
  }'
```

---

## 🛠️ **Error Responses**

### **Validation Errors**

```json
{
  "data": {
    "register": {
      "success": false,
      "message": "Đăng ký thất bại",
      "user": null,
      "errors": {
        "username": "Tên đăng nhập đã tồn tại",
        "email": "Email không hợp lệ",
        "password": "Mật khẩu quá yếu",
        "general": null
      }
    }
  }
}
```

### **Authentication Errors**

```json
{
  "data": {
    "login": {
      "success": false,
      "message": "Đăng nhập thất bại",
      "user": null,
      "tokens": null,
      "errors": {
        "username": null,
        "password": "Mật khẩu không chính xác",
        "general": "Tài khoản đã bị khóa"
      }
    }
  }
}
```

### **Authorization Errors**

```json
{
  "errors": [
    {
      "message": "You do not have permission to perform this action",
      "locations": [{ "line": 2, "column": 3 }],
      "path": ["userProfile"]
    }
  ],
  "data": {
    "userProfile": null
  }
}
```

---

## 🔧 **Testing Tools**

### **GraphQL Playground**

```
http://localhost:8000/graphql/
```

### **Postman Collection**

Import this collection for easy testing:

```json
{
  "info": {
    "name": "SHOEX GraphQL API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "auth": {
    "type": "bearer",
    "bearer": [
      {
        "key": "token",
        "value": "{{jwt_token}}",
        "type": "string"
      }
    ]
  }
}
```

---

## ⚙️ **Environment Variables**

### **Development**

```env
GRAPHQL_ENDPOINT=http://localhost:8000/graphql/
JWT_SECRET_KEY=your-secret-key
JWT_EXPIRATION=86400
MEDIA_URL=/media/
```

### **Production**

```env
GRAPHQL_ENDPOINT=https://api.shoex.com/graphql/
JWT_SECRET_KEY=production-secret-key
JWT_EXPIRATION=3600
MEDIA_URL=https://cdn.shoex.com/media/
```

---

## 📋 **Status Codes**

| Code | Description                          |
| ---- | ------------------------------------ |
| 200  | Success - Request completed          |
| 400  | Bad Request - Invalid input          |
| 401  | Unauthorized - Invalid token         |
| 403  | Forbidden - Insufficient permissions |
| 404  | Not Found - Resource not found       |
| 500  | Internal Server Error                |

---

## 🚀 **Quick Start**

1. **Đăng ký tài khoản mới**
2. **Đăng nhập để lấy JWT token**
3. **Sử dụng token trong header Authorization**
4. **Gọi các API cần authentication**

### **Example Workflow**

```bash
# 1. Register
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -d '{"query":"mutation{register(input:{fullName:\"Test User\",username:\"testuser\",email:\"test@example.com\",password:\"password123\"}){success user{id username} errors{general}}}"}'

# 2. Login
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -d '{"query":"mutation{login(input:{username:\"testuser\",password:\"password123\"}){success tokens{accessToken} errors{general}}}"}'

# 3. Use token for authenticated requests
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"query":"query{userProfile{user{id username email fullName}}}"}'
```
