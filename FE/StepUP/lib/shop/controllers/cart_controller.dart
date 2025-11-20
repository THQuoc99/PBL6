import 'dart:convert';
import 'package:get/get.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter_app/shop/models/cart_item_model.dart';

class CartController extends GetxController {
  static CartController get instance => Get.find();

  final isLoading = false.obs;
  final cartItems = <CartItemModel>[].obs;
  final totalAmount = 0.0.obs; // Tổng tiền (chỉ tính các món được chọn)

  final String baseUrl = "http://10.0.2.2:8000/api/cart";

  @override
  void onInit() {
    fetchCart();
    super.onInit();
  }

  // ✅ HÀM MỚI: Tính lại tổng tiền dựa trên các món được tích chọn
  void updateCartTotal() {
    double total = 0.0;
    for (var item in cartItems) {
      if (item.isSelected.value) {
        total += item.price * item.quantity;
      }
    }
    totalAmount.value = total;
  }

  // ✅ HÀM MỚI: Xử lý khi tích/bỏ tích một món
  void toggleSelection(int index) {
    cartItems[index].isSelected.toggle(); // Đảo ngược trạng thái true/false
    updateCartTotal(); // Tính lại tiền ngay lập tức
  }
  
  // ✅ HÀM MỚI: Chọn tất cả / Bỏ chọn tất cả (Nếu cần dùng sau này)
  void toggleAll(bool value) {
    for (var item in cartItems) {
      item.isSelected.value = value;
    }
    updateCartTotal();
  }

  // ✅ HÀM MỚI: Lấy danh sách các món ĐƯỢC CHỌN để checkout
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
        // Sau khi load xong, tính lại tổng tiền theo logic chọn (mặc định chọn hết)
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

      if (response.statusCode == 200) {
        Get.snackbar('Thành công', 'Đã thêm vào giỏ hàng', 
          snackPosition: SnackPosition.BOTTOM);
        fetchCart(); // Tải lại giỏ để cập nhật số lượng trên icon (nếu có)
      } else {
        Get.snackbar('Lỗi', 'Không thể thêm: ${response.body}');
      }
    } catch (e) {
      print(e);
    }
  }

  Future<void> updateQuantity(int itemId, int newQuantity) async {
    // Optimistic update (Cập nhật UI trước cho mượt)
    final index = cartItems.indexWhere((item) => item.itemId == itemId);
    if (index != -1) {
      cartItems[index].quantity = newQuantity;
      cartItems.refresh(); // Báo cho UI biết list đã thay đổi
      updateCartTotal(); // ✅ Tính lại tiền ngay lập tức
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
      
      // Không cần fetchCart lại nếu chỉ update số lượng để tránh giật lag
    } catch (e) {
      print("Lỗi update: $e");
      fetchCart(); // Revert nếu lỗi
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
      
      // Xóa local trước cho mượt
      cartItems.removeWhere((item) => item.itemId == itemId);
      updateCartTotal();
      
      Get.snackbar('Thành công', 'Đã xóa sản phẩm');
    } catch (e) {
      print("Lỗi xóa: $e");
      fetchCart();
    }
  }
}