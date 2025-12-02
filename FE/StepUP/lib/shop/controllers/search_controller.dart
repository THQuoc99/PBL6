import 'dart:convert';
import 'package:get/get.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_app/shop/models/product_model.dart';

class SearchController extends GetxController {
  static SearchController get instance => Get.find();

  final searchText = ''.obs;
  final searchResults = <ProductModel>[].obs;
  final isLoading = false.obs;

  // Giả sử API tìm kiếm của bạn là: /api/products/?search=keyword
  // Hoặc nếu API list products hỗ trợ filter
  final String baseUrl = "http://10.0.2.2:8000/api/products"; 

  // Hàm tìm kiếm
  Future<void> searchProducts(String query) async {
    if (query.isEmpty) {
      searchResults.clear();
      return;
    }

    searchText.value = query;
    isLoading.value = true;

    try {
      // Gọi API với tham số search (Tùy backend của bạn cấu hình filter như nào)
      // Ví dụ Django Rest Framework thường dùng ?search=
      final response = await http.get(Uri.parse('$baseUrl/?search=$query')); 

      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(utf8.decode(response.bodyBytes));
        searchResults.assignAll(
          data.map((e) => ProductModel.fromJson(e)).toList(),
        );
      } else {
        // Xử lý lỗi nếu cần
        searchResults.clear();
      }
    } catch (e) {
      print("Search Error: $e");
      searchResults.clear();
    } finally {
      isLoading.value = false;
    }
  }
}