import 'dart:convert';
import 'package:get/get.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_app/shop/models/product_model.dart';

class ProductController extends GetxController {
  static ProductController get instance => Get.find();

  final isLoading = false.obs;
  
  // URL API (Thay đổi nếu đã deploy lên server thật)
  final String baseUrl = "http://10.0.2.2:8000"; 

  /// Hàm lấy chi tiết 1 sản phẩm theo ID
  Future<ProductModel?> fetchProductById(int id) async {
    try {
      isLoading.value = true;
      
      // Gọi API: GET /api/products/{id}/
      final response = await http.get(Uri.parse('$baseUrl/api/products/$id/'));

      if (response.statusCode == 200) {
        // Decode UTF8 để hiển thị tiếng Việt không bị lỗi font
        final data = json.decode(utf8.decode(response.bodyBytes));
        return ProductModel.fromJson(data);
      } else {
        print("❌ Lỗi tải sản phẩm ID $id: ${response.statusCode}");
        return null;
      }
    } catch (e) {
      print("❌ Exception tải sản phẩm: $e");
      return null;
    } finally {
      isLoading.value = false;
    }
  }
}