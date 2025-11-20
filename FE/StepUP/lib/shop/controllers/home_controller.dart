import 'dart:convert';
import 'package:get/get.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_app/shop/models/category_model.dart';
import 'package:flutter_app/shop/models/product_model.dart';

class HomeController extends GetxController {
  static HomeController get instance => Get.find();

  final carousalCurrentIndex = 0.obs;

  void updatePageIndicator(index) {
    carousalCurrentIndex.value = index;
  }

  final isLoading = false.obs;
  final categoryList = <CategoryModel>[].obs;
  final productList = <ProductModel>[].obs;

  // URL API (Dùng 10.0.2.2 cho máy ảo Android)
  final String baseUrl = "http://10.0.2.2:8000"; 

  @override
  void onInit() {
    fetchHomeData();
    super.onInit();
  }

  Future<void> fetchHomeData() async {
    try {
      isLoading.value = true;
      await Future.wait([
        fetchCategories(),
        fetchProducts(),
      ]);
    } catch (e) {
      print("❌ Lỗi tải dữ liệu Home: $e");
    } finally {
      isLoading.value = false;
    }
  }

  Future<void> fetchCategories() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/api/categories/'));
      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(utf8.decode(response.bodyBytes));
        categoryList.value = data.map((e) => CategoryModel.fromJson(e)).toList();
      }
    } catch (e) {
      print('❌ Error fetching categories: $e');
    }
  }

  Future<void> fetchProducts() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/api/products/'));
      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(utf8.decode(response.bodyBytes));
        // Lấy 6 sản phẩm đầu tiên
        productList.value = data.map((e) => ProductModel.fromJson(e)).take(6).toList();
      }
    } catch (e) {
      print('❌ Error fetching products: $e');
    }
  }
}