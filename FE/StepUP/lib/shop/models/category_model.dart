class CategoryModel {
  final int id;
  final String name;
  final String? image;
  final String? description; // Thêm description cho đủ

  CategoryModel({
    required this.id, 
    required this.name, 
    this.image,
    this.description
  });

  factory CategoryModel.fromJson(Map<String, dynamic> json) {
    return CategoryModel(
      id: json['category_id'] ?? 0,
      name: json['name'] ?? '',
      image: json['image'], 
      description: json['description'],
    );
  }
}