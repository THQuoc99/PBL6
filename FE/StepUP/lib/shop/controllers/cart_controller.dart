import 'dart:convert';
import 'package:get/get.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter_app/shop/models/cart_item_model.dart';

class CartController extends GetxController {
  static CartController get instance => Get.find();

  final isLoading = false.obs;
  final cartItems = <CartItemModel>[].obs;
  final totalAmount = 0.0.obs; 

  final String baseUrl = "http://10.0.2.2:8000/api/cart";

  @override
  void onInit() {
    fetchCart();
    super.onInit();
  }

  void updateCartTotal() {
    double total = 0.0;
    for (var item in cartItems) {
      if (item.isSelected.value) {
        // Ưu tiên dùng subTotal backend tính sẵn, nếu không thì tự nhân
        total += (item.subTotal > 0) ? item.subTotal : (item.price * item.quantity);
      }
    }
    totalAmount.value = total;
  }

  void toggleSelection(int index) {
    cartItems[index].isSelected.toggle();
    updateCartTotal();
  }
  
  void toggleAll(bool value) {
    for (var item in cartItems) {
      item.isSelected.value = value;
    }
    updateCartTotal();
  }

  // Helper lấy danh sách để Checkout
  List<CartItemModel> get selectedItems => cartItems.where((item) => item.isSelected.value).toList();

  Future<void> fetchCart() async {
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
        final data = json.decode(utf8.decode(response.bodyBytes));
        if (data['items'] != null) {
          final List items = data['items'];
          cartItems.value = items.map((e) => CartItemModel.fromJson(e)).toList();
        }
        updateCartTotal();
      }
    } catch (e) {
      print("❌ Lỗi tải giỏ: $e");
    } finally {
      isLoading.value = false;
    }
  }

   Future<void> addToCart(int variantId, int quantity) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('token');
      if (token == null) {
        Get.snackbar('Lỗi', 'Vui lòng đăng nhập');
        return;
      }

      final response = await http.post(
        Uri.parse('$baseUrl/add/'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token'
        },
        body: json.encode({
          'variant_id': variantId,
          'quantity': quantity
        }),
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        Get.snackbar('Thành công', 'Đã thêm vào giỏ hàng', 
          snackPosition: SnackPosition.BOTTOM);
        fetchCart(); 
      } else {
        var msg = json.decode(response.body)['error'] ?? 'Lỗi không xác định';
        Get.snackbar('Lỗi', msg);
      }
    } catch (e) {
      print(e);
    }
  }

  Future<void> updateQuantity(int itemId, int newQuantity) async {
    // Optimistic update
    final index = cartItems.indexWhere((item) => item.itemId == itemId);
    if (index != -1) {
      cartItems[index].quantity = newQuantity;
      cartItems.refresh(); 
      updateCartTotal(); 
    }

    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('token');
      
      await http.patch(
        Uri.parse('$baseUrl/$itemId/update_quantity/'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token'
        },
        body: json.encode({'quantity': newQuantity}),
      );
    } catch (e) {
      print("Lỗi update: $e");
      fetchCart(); // Revert
    }
  }

  Future<void> removeItem(int itemId) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('token');

      await http.delete(
        Uri.parse('$baseUrl/$itemId/remove/'),
        headers: {'Authorization': 'Bearer $token'},
      );
      
      cartItems.removeWhere((item) => item.itemId == itemId);
      updateCartTotal();
      
      Get.snackbar('Thành công', 'Đã xóa sản phẩm');
    } catch (e) {
      print("Lỗi xóa: $e");
      fetchCart();
    }
  }
}