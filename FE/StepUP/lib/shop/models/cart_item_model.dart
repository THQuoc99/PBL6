import 'package:get/get.dart'; // Import Get để dùng Rx

class CartItemModel {
  final int itemId;
  final int productId;
  final String productName;
  final String brand;
  final double price;
  int quantity;
  final String? image;
  final Map<String, dynamic> attributes;
  
  // ✅ THÊM: Biến trạng thái tích chọn (Mặc định là true - chọn tất cả)
  // Dùng RxBool để UI tự cập nhật khi giá trị thay đổi
  RxBool isSelected = true.obs; 

  CartItemModel({
    required this.itemId,
    required this.productId,
    required this.productName,
    required this.brand,
    required this.price,
    required this.quantity,
    this.image,
    required this.attributes,
    bool selected = true,
  }) {
    isSelected.value = selected;
  }

  factory CartItemModel.fromJson(Map<String, dynamic> json) {
    return CartItemModel(
      itemId: json['item_id'],
      productId: json['product_id'],
      productName: json['product_name'] ?? 'Unknown Product',
      brand: json['brand'] ?? '',
      
      // ✅ SỬA LỖI 0$: Backend trả về 'price', nhưng code cũ đọc 'unit_price'
      // Ta sửa thành đọc cả 2, cái nào có thì lấy.
      price: double.tryParse(json['price']?.toString() ?? json['unit_price']?.toString() ?? '0') ?? 0.0,
      
      quantity: json['quantity'] ?? 1,
      image: json['image'],
      attributes: json['attributes'] is Map ? json['attributes'] : {},
    );
  }
}