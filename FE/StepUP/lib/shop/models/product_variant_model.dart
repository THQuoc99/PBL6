import 'dart:convert'; // Import để dùng json.decode nếu cần

class ProductVariantModel {
  final int id;
  final String sku;
  final double price;
  final int stock;
  final Map<String, String> attributes;

  ProductVariantModel({
    required this.id,
    required this.sku,
    required this.price,
    required this.stock,
    required this.attributes,
  });

  factory ProductVariantModel.fromJson(Map<String, dynamic> json) {
    // Xử lý an toàn cho attributes
    Map<String, String> attrs = {};
    
    try {
      var options = json['option_combinations'];
      if (options != null) {
        // Nếu backend trả về String (VD: "{\"Color\": \"Red\"}"), cần decode
        if (options is String) {
          options = jsonDecode(options);
        }
        
        // Chuyển đổi sang Map<String, String>
        if (options is Map) {
          options.forEach((key, value) {
            attrs[key.toString()] = value.toString();
          });
        }
      }
    } catch (e) {
      print("Lỗi parse attributes: $e");
    }

    return ProductVariantModel(
      id: json['variant_id'] ?? 0,
      sku: json['sku'] ?? '',
      price: double.tryParse(json['price'].toString()) ?? 0.0,
      stock: int.tryParse(json['stock'].toString()) ?? 0,
      attributes: attrs,
    );
  }
}