import 'dart:convert';
import 'package:get/get.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_app/shop/models/product_model.dart';

class CategoryProductsController extends GetxController {
  final isLoading = false.obs;
  final products = <ProductModel>[].obs;
  
  // URL API
  final String baseUrl = "http://10.0.2.2:8000/api/products"; 

  // Hàm lấy sản phẩm theo Category ID
  Future<void> fetchProductsByCategory(int categoryId) async {
    try {
      isLoading.value = true;
      // Gọi API lọc theo category (Backend đã hỗ trợ ?category=ID)
      final response = await http.get(Uri.parse('$baseUrl/?category=$categoryId'));
      
      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(utf8.decode(response.bodyBytes));
        products.value = data.map((e) => ProductModel.fromJson(e)).toList();
      } else {
        print("Lỗi tải sản phẩm danh mục: ${response.statusCode}");
      }
    } catch (e) {
      print("Exception Category Products: $e");
    } finally {
      isLoading.value = false;
    }
  }
}