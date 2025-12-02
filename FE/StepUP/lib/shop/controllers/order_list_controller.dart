import 'dart:convert';
import 'package:get/get.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter_app/shop/models/order_model.dart';

class OrderListController extends GetxController {
  static OrderListController get instance => Get.find();

  final isLoading = false.obs;
  final orders = <OrderModel>[].obs;
  final String baseUrl = "http://10.0.2.2:8000/api/orders"; 

  @override
  void onInit() {
    fetchUserOrders();
    super.onInit();
  }

  Future<void> fetchUserOrders() async {
    try {
      isLoading.value = true;
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('token');
      
      if (token == null) return;

      final response = await http.get(
        Uri.parse('$baseUrl/'),
        headers: {'Authorization': 'Bearer $token'},
      );

      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(utf8.decode(response.bodyBytes));
        orders.value = data.map((e) => OrderModel.fromJson(e)).toList();
      } else {
        print("Lỗi tải đơn hàng: ${response.statusCode}");
      }
    } catch (e) {
      print("Exception tải đơn hàng: $e");
    } finally {
      isLoading.value = false;
    }
  }
}