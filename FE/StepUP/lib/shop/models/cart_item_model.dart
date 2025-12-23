import 'dart:convert';
import 'package:get/get.dart';

class CartItemModel {
  // ... các trường khác (productId, quantity...)
  final int itemId;
  final int productId;
  final String productName;
  final String brand;
  final double price;
  final double subTotal; 
  int quantity;
  final String? image;
  final Map<String, dynamic> attributes;
  final Map<String, String> selectedVariation;
  
  // Store info for shipping calculation
  final String? storeId;
  final String? storeName;
  final Map<String, dynamic>? storeAddress;
  
  // Biến trạng thái UI (GetX)
  RxBool isSelected = true.obs; 

  CartItemModel({
    required this.itemId,
    required this.productId,
    required this.productName,
    required this.brand,
    required this.price,
    required this.subTotal,
    required this.quantity,
    this.image,
    required this.attributes,
    required this.selectedVariation,
    this.storeId,
    this.storeName,
    this.storeAddress,
    bool selected = true,
  }) {
    isSelected.value = selected;
  }

  factory CartItemModel.fromJson(Map<String, dynamic> json) {
    return CartItemModel(
      itemId: json['item_id'] ?? 0,
      productId: json['product_id'] ?? 0,
      productName: json['product_name'] ?? 'Sản phẩm',
      brand: json['brand'] ?? '',
      
      // ✅ SỬA LẠI: Thêm json['attributes'] vào luồng kiểm tra để chắc chắn lấy được dữ liệu
      selectedVariation: _parseAttributes(
          json['selected_variation'] ?? json['option_combinations'] ?? json['attributes']
      ),
      
      price: double.tryParse(json['price']?.toString() ?? '0') ?? 0.0,
      
      // Backend trả về sub_total
      subTotal: double.tryParse(json['sub_total']?.toString() ?? '0') ?? 0.0,
      
      quantity: json['quantity'] ?? 1,
      image: json['image'], // Backend trả về URL đầy đủ
      
      // Parse JSON Attributes (Giữ lại để tương thích ngược nếu cần)
      attributes: json['attributes'] is Map 
          ? Map<String, dynamic>.from(json['attributes']) 
          : {},
      
      // Store info
      storeId: json['store_id'],
      storeName: json['store_name'],
      storeAddress: json['store_address'] is Map 
          ? Map<String, dynamic>.from(json['store_address'])
          : null,
    );
  }

  // Helper: Hiển thị biến thể (VD: "Đỏ, 40")
  String get variantString {
    if (selectedVariation.isEmpty) return '';
    return selectedVariation.values.join(', ');
  }

  static Map<String, String> _parseAttributes(dynamic rawData) {
    if (rawData == null) return {};

    // 1. Nếu là Map -> Dùng luôn
    if (rawData is Map) {
      return rawData.map((key, value) => MapEntry(key.toString(), value.toString()));
    }

    // 2. Nếu là String (Lỗi DB) -> Decode trước
    if (rawData is String) {
      try {
        final decoded = json.decode(rawData);
        if (decoded is Map) {
          return decoded.map((key, value) => MapEntry(key.toString(), value.toString()));
        }
      } catch (e) {
        print("⚠️ Lỗi parse Attribute Cart: $e");
      }
    }
    return {};
  }
}