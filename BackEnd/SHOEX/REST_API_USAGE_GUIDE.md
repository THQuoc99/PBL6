# Hướng dẫn sử dụng REST API Upload Ảnh

## 📋 Các Endpoints có sẵn:

### 1. **Upload ảnh đơn lẻ cho sản phẩm**

```
POST /api/products/upload-image/
Content-Type: multipart/form-data
```

**Body:**

- `product_id`: ID sản phẩm (required)
- `image`: File ảnh (required)
- `is_thumbnail`: Boolean - có phải thumbnail không (optional)
- `alt_text`: Mô tả ảnh (optional)
- `display_order`: Thứ tự hiển thị (optional)

**Response:**

```json
{
  "message": "Upload thành công",
  "image": {
    "id": "img_123",
    "url": "http://localhost:8000/media/products/product_1/image.jpg",
    "is_thumbnail": true,
    "alt_text": "Giày Nike Air Max",
    "display_order": 1
  }
}
```

---

### 2. **Upload nhiều ảnh cùng lúc**

```
POST /api/products/upload-multiple-images/
Content-Type: multipart/form-data
```

**Body:**

- `product_id`: ID sản phẩm (required)
- `images`: Array files ảnh - tối đa 10 ảnh (required)

**Response:**

```json
{
  "message": "Upload thành công 3 ảnh",
  "images": [
    {
      "id": "img_124",
      "url": "http://localhost:8000/media/products/product_1/image1.jpg",
      "alt_text": "Giày Nike - Ảnh 1",
      "display_order": 1
    },
    {
      "id": "img_125",
      "url": "http://localhost:8000/media/products/product_1/image2.jpg",
      "alt_text": "Giày Nike - Ảnh 2",
      "display_order": 2
    }
  ]
}
```

---

### 3. **Upload ảnh cho attribute option (màu sắc)**

```
POST /api/products/attributes/options/upload-image/
Content-Type: multipart/form-data
```

**Body:**

- `option_id`: ID của option (required)
- `image`: File ảnh (required)
- `value`: Giá trị option (optional)
- `value_code`: Mã màu (optional)

**Response:**

```json
{
  "message": "Upload thành công",
  "option": {
    "id": "opt_456",
    "value": "Đỏ",
    "value_code": "#FF0000",
    "image_url": "http://localhost:8000/media/products/attributes/red.jpg",
    "display_order": 1
  }
}
```

---

### 4. **Lấy danh sách ảnh của sản phẩm**

```
GET /api/products/{product_id}/images/
```

**Response:**

```json
{
  "product_id": 1,
  "product_name": "Giày Nike Air Max",
  "images": [
    {
      "id": "img_123",
      "url": "http://localhost:8000/media/products/product_1/thumbnail.jpg",
      "is_thumbnail": true,
      "alt_text": "Giày Nike Air Max",
      "display_order": 0,
      "created_at": "2025-10-05T10:30:00Z"
    }
  ]
}
```

---

### 5. **Xóa ảnh sản phẩm**

```
DELETE /api/products/images/{image_id}/
```

**Response:**

```json
{
  "message": "Xóa ảnh thành công"
}
```

---

## 🔧 Cách sử dụng với các tools:

### **cURL:**

```bash
# Upload ảnh đơn lẻ
curl -X POST \
  http://localhost:8000/api/products/upload-image/ \
  -H 'Content-Type: multipart/form-data' \
  -F 'product_id=1' \
  -F 'image=@/path/to/image.jpg' \
  -F 'is_thumbnail=true' \
  -F 'alt_text=Ảnh thumbnail'

# Upload nhiều ảnh
curl -X POST \
  http://localhost:8000/api/products/upload-multiple-images/ \
  -H 'Content-Type: multipart/form-data' \
  -F 'product_id=1' \
  -F 'images=@/path/to/image1.jpg' \
  -F 'images=@/path/to/image2.jpg' \
  -F 'images=@/path/to/image3.jpg'

# Lấy danh sách ảnh
curl -X GET http://localhost:8000/api/products/1/images/

# Xóa ảnh
curl -X DELETE http://localhost:8000/api/products/images/img_123/
```

### **Postman:**

1. **Method**: POST
2. **URL**: `http://localhost:8000/api/products/upload-image/`
3. **Headers**: Không cần set Content-Type (auto)
4. **Body**:
   - Chọn `form-data`
   - Thêm key `product_id` với value `1`
   - Thêm key `image` với type `File`, chọn file ảnh
   - Thêm key `is_thumbnail` với value `true`

### **JavaScript/Fetch:**

```javascript
// Upload ảnh đơn lẻ
const uploadImage = async (productId, imageFile) => {
  const formData = new FormData();
  formData.append("product_id", productId);
  formData.append("image", imageFile);
  formData.append("is_thumbnail", "true");

  const response = await fetch("/api/products/upload-image/", {
    method: "POST",
    body: formData,
  });

  return await response.json();
};

// Upload nhiều ảnh
const uploadMultipleImages = async (productId, imageFiles) => {
  const formData = new FormData();
  formData.append("product_id", productId);

  imageFiles.forEach((file) => {
    formData.append("images", file);
  });

  const response = await fetch("/api/products/upload-multiple-images/", {
    method: "POST",
    body: formData,
  });

  return await response.json();
};

// Lấy danh sách ảnh
const getProductImages = async (productId) => {
  const response = await fetch(`/api/products/${productId}/images/`);
  return await response.json();
};
```

### **React Form:**

```jsx
import React, { useState } from "react";

const ImageUploadForm = ({ productId }) => {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [uploading, setUploading] = useState(false);

  const handleFileChange = (e) => {
    setSelectedFiles([...e.target.files]);
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    setUploading(true);

    const formData = new FormData();
    formData.append("product_id", productId);

    selectedFiles.forEach((file) => {
      formData.append("images", file);
    });

    try {
      const response = await fetch("/api/products/upload-multiple-images/", {
        method: "POST",
        body: formData,
      });

      const result = await response.json();
      console.log("Upload result:", result);
    } catch (error) {
      console.error("Upload error:", error);
    } finally {
      setUploading(false);
    }
  };

  return (
    <form onSubmit={handleUpload}>
      <input
        type="file"
        multiple
        accept="image/*"
        onChange={handleFileChange}
      />
      <button type="submit" disabled={uploading}>
        {uploading ? "Đang upload..." : "Upload ảnh"}
      </button>
    </form>
  );
};
```

---

## ⚠️ Lưu ý quan trọng:

### **Validation:**

- File size tối đa: 10MB
- Formats hỗ trợ: JPG, PNG, WebP
- Tối đa 10 ảnh/lần upload multiple
- Tự động resize để tối ưu

### **Security:**

- Validate file type nghiêm ngặt
- Scan malware nếu cần
- Rate limiting cho upload endpoints

### **Performance:**

- Ảnh được tự động compress
- Thumbnail được tạo riêng
- CDN integration nếu cần

### **URL Structure:**

- Development: `http://localhost:8000/media/...`
- Production: `https://yourdomain.com/media/...`

**Cách này cho phép upload ảnh qua REST API song song với GraphQL! 🚀**
