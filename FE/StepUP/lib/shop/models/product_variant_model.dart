import 'dart:convert'; // 1. Nhớ import thư viện này

class ProductVariantModel {
  final int id;
  final int productId;
  final String sku;
  final double price;
  final int stock;
  final Map<String, String> attributeCombinations;

  ProductVariantModel({
    required this.id,
    required this.productId,
    required this.sku,
    required this.price,
    required this.stock,
    required this.attributeCombinations,
  });

  factory ProductVariantModel.fromJson(Map<String, dynamic> json) {
    return ProductVariantModel(
      id: json['variant_id'] ?? json['id'] ?? 0,
      productId: json['product_id'] ?? 0,
      sku: json['sku'] ?? '',
      price: double.tryParse(json['price']?.toString() ?? '0') ?? 0.0,
      stock: json['stock'] ?? 0,
      
      // Gọi hàm parse thông minh hơn
      attributeCombinations: _parseAttributes(json['option_combinations']),
    );
  }

  // --- HÀM XỬ LÝ DỮ LIỆU BỊ LỖI FORMAT ---
  static Map<String, String> _parseAttributes(dynamic rawData) {
    if (rawData == null) return {};

    // TRƯỜNG HỢP 1: Dữ liệu chuẩn là Map -> Dùng luôn
    if (rawData is Map) {
      return rawData.map((key, value) => MapEntry(key.toString(), value.toString()));
    }

    // TRƯỜNG HỢP 2: Dữ liệu bị lưu thành String (như trong DB của bạn) -> Decode trước
    if (rawData is String) {
      try {
        // decode: "{\"Size\":\"26\"}" -> {"Size": "26"}
        final decoded = json.decode(rawData);
        
        // Sau khi decode, nếu nó ra Map thì convert tiếp
        if (decoded is Map) {
          return decoded.map((key, value) => MapEntry(key.toString(), value.toString()));
        }
      } catch (e) {
        print("⚠️ Lỗi parse JSON Attribute: $e");
      }
    }

    return {};
  }

  Map<String, dynamic> toJson() => {
    'variant_id': id,
    'product_id': productId,
    'sku': sku,
    'price': price,
    'stock': stock,
    'option_combinations': attributeCombinations,
  };

  String get displayName {
    if (attributeCombinations.isEmpty) return sku;
    return attributeCombinations.values.join(' - ');
  }
}