import 'product_variant_model.dart';

class ProductModel {
  final int id;
  final String name;
  final double price;
  final String? image;
  final String description;
  final String storeName;
  final String storeId; // ✅ MỚI THÊM
  final double rating;
  final int reviewCount;
  final List<ProductVariantModel> variants;

  ProductModel({
    required this.id,
    required this.name,
    required this.price,
    this.image,
    required this.description,
    this.storeName = '',
    this.storeId = '', // ✅ Mặc định rỗng
    this.rating = 0.0,
    this.reviewCount = 0,
    this.variants = const [],
  });

  factory ProductModel.fromJson(Map<String, dynamic> json) {
    List<ProductVariantModel> variantsList = [];
    if (json['variants'] != null && json['variants'] is List) {
      variantsList = (json['variants'] as List)
          .map((item) => ProductVariantModel.fromJson(item))
          .toList();
    }

    double parsedPrice = 0.0;
    if (json['base_price'] != null) {
      parsedPrice = double.tryParse(json['base_price'].toString()) ?? 0.0;
    } else if (json['price'] != null) {
      parsedPrice = double.tryParse(json['price'].toString()) ?? 0.0;
    }

    return ProductModel(
      id: json['product_id'] ?? json['id'] ?? 0,
      name: json['name'] ?? '',
      price: parsedPrice,
      image: json['image'],
      description: json['description'] ?? '',
      storeName: json['store_name'] ?? '',
      storeId: json['store_id'] ?? '', // ✅ Map với field từ backend
      rating: double.tryParse(json['rating']?.toString() ?? '0') ?? 0.0,
      reviewCount: json['review_count'] ?? 0,
      variants: variantsList,
    );
  }
}