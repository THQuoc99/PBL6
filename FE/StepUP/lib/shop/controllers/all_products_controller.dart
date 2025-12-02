import 'dart:convert';
import 'package:get/get.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_app/shop/models/product_model.dart';

class AllProductsController extends GetxController {
  static AllProductsController get instance => Get.find();

  final isLoading = false.obs;
  final productList = <ProductModel>[].obs;
  final selectedSortOption = 'Name'.obs;
  final String baseUrl = "http://10.0.2.2:8000"; 

  @override
  void onInit() {
    fetchAllProducts();
    super.onInit();
  }

  Future<void> fetchAllProducts() async {
    try {
      isLoading.value = true;
      final response = await http.get(Uri.parse('$baseUrl/api/products/'));
      
      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(utf8.decode(response.bodyBytes));
        productList.value = data.map((e) => ProductModel.fromJson(e)).toList();
        sortProducts(selectedSortOption.value);
      }
    } catch (e) {
      print("❌ Lỗi tải SP: $e");
    } finally {
      isLoading.value = false;
    }
  }

  void sortProducts(String sortOption) {
    selectedSortOption.value = sortOption;
    switch (sortOption) {
      case 'Name':
        productList.sort((a, b) => a.name.compareTo(b.name));
        break;
      case 'Price': 
        productList.sort((a, b) => a.price.compareTo(b.price));
        break;
      case 'Sale':
        productList.sort((a, b) => b.price.compareTo(a.price));
        break;
    }
  }
}