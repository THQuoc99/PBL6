import 'dart:convert';
import 'package:get/get.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_app/shop/models/product_model.dart';

class AllProductsController extends GetxController {
  static AllProductsController get instance => Get.find();

  final isLoading = false.obs;
  final productList = <ProductModel>[].obs;
  // Biến lưu giá trị sort hiện tại (Mặc định là Name)
  final selectedSortOption = 'Name'.obs;

  // URL API
  final String baseUrl = "http://10.0.2.2:8000"; 

  @override
  void onInit() {
    fetchAllProducts();
    super.onInit();
  }

  Future<void> fetchAllProducts() async {
    try {
      isLoading.value = true;
      // Gọi API lấy tất cả sản phẩm
      final response = await http.get(Uri.parse('$baseUrl/api/products/'));
      
      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(utf8.decode(response.bodyBytes));
        productList.value = data.map((e) => ProductModel.fromJson(e)).toList();
        
        // Sau khi tải xong, sắp xếp theo option mặc định
        sortProducts(selectedSortOption.value);
      } else {
        Get.snackbar('Lỗi', 'Không tải được sản phẩm: ${response.statusCode}');
      }
    } catch (e) {
      print("❌ Lỗi tải All Products: $e");
      Get.snackbar('Lỗi', 'Có lỗi xảy ra khi tải dữ liệu.');
    } finally {
      isLoading.value = false;
    }
  }

  // Hàm sắp xếp sản phẩm
  void sortProducts(String sortOption) {
    selectedSortOption.value = sortOption;
    
    switch (sortOption) {
      case 'Name':
        productList.sort((a, b) => a.name.compareTo(b.name));
        break;
      case 'Price': // Giá thấp -> cao
        productList.sort((a, b) => a.price.compareTo(b.price));
        break;
      case 'Sale': // Giả sử Sale là giá cao -> thấp (hoặc logic khác tùy bạn)
        productList.sort((a, b) => b.price.compareTo(a.price));
        break;
      default:
        productList.sort((a, b) => a.name.compareTo(b.name));
    }
  }
}