import 'product_variant_model.dart';

class ProductModel {
  final int id;
  final String name;
  final double price;
  final String? image;
  final String description;
  // ✅ Đảm bảo biến này không bao giờ null
  final List<ProductVariantModel> variants;

  ProductModel({
    required this.id, 
    required this.name, 
    required this.price, 
    this.image,
    required this.description,
    this.variants = const [], 
  });

  factory ProductModel.fromJson(Map<String, dynamic> json) {
    // 1. Tạo list rỗng mặc định
    List<ProductVariantModel> variantsList = [];

    // 2. Kiểm tra kỹ dữ liệu từ API
    if (json['variants'] != null && json['variants'] is List) {
      try {
        variantsList = (json['variants'] as List)
            .map((item) => ProductVariantModel.fromJson(item))
            .toList();
      } catch (e) {
        print("Lỗi parse variants: $e");
      }
    }

    return ProductModel(
      id: json['product_id'] ?? json['id'] ?? 0,
      name: json['name'] ?? '',
      price: double.tryParse(json['base_price'].toString()) ?? double.tryParse(json['price'].toString()) ?? 0.0,
      image: json['image'],
      description: json['description'] ?? '',
      // ✅ Gán list đã xử lý (không bao giờ null)
      variants: variantsList, 
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'price': price,
      'image': image,
      'description': description,
    };
  }
}