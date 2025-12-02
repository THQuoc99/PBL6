import 'dart:convert';
import 'package:flutter/material.dart'; // Cần import để dùng Colors
import 'package:get/get.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter_app/shop/models/product_model.dart';
import 'package:flutter_app/shop/controllers/user_controller.dart';

class WishlistController extends GetxController {
  static WishlistController get instance => Get.find();

  final RxList<ProductModel> favorites = <ProductModel>[].obs;
  final isLoading = false.obs;
  
  // Lấy UserController để biết ai đang đăng nhập
  final userController = Get.find<UserController>();

  // ✅ BASE URL (Thay bằng IP/Domain thật của bạn)
  final String baseUrl = "http://10.0.2.2:8000/api/cart/wishlist"; 

  @override
  void onInit() {
    super.onInit();
    // 1. Tải danh sách lần đầu
    fetchWishlist();
    
    // 2. TỰ ĐỘNG: Lắng nghe sự thay đổi của UserID
    ever(userController.userID, (_) {
      fetchWishlist();
    });
  }

  // --- 1. TẢI DANH SÁCH TỪ API ---
  Future<void> fetchWishlist() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('token');

    if (token == null) {
      favorites.clear();
      return;
    }

    try {
      isLoading.value = true;
      final response = await http.get(
        Uri.parse('$baseUrl/'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(utf8.decode(response.bodyBytes));
        favorites.assignAll(
          data.map((e) => ProductModel.fromJson(e)).toList(),
        );
      } else {
        print("Lỗi tải wishlist: ${response.statusCode}");
      }
    } catch (e) {
      print("Exception wishlist: $e");
    } finally {
      isLoading.value = false;
    }
  }

  // --- 2. KIỂM TRA TRẠNG THÁI ---
  bool isFavorite(int productId) {
    return favorites.any((product) => product.id == productId);
  }

  // --- 3. THÊM / XÓA (GỌI API) ---
  Future<void> toggleFavorite(ProductModel product) async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('token');

    if (token == null) {
      _safeSnackbar('Thông báo', 'Vui lòng đăng nhập để lưu sản phẩm yêu thích', isError: true);
      return;
    }

    // --- OPTIMISTIC UPDATE (Cập nhật UI trước) ---
    bool currentlyFavorite = isFavorite(product.id);
    
    if (currentlyFavorite) {
      favorites.removeWhere((p) => p.id == product.id);
      _safeSnackbar('Đã xóa', 'Đã xóa khỏi mục yêu thích');
    } else {
      favorites.add(product);
      _safeSnackbar('Đã thêm', 'Đã thêm vào mục yêu thích', isSuccess: true);
    }

    // --- GỌI API ĐỒNG BỘ ---
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/toggle/'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: jsonEncode({'product_id': product.id}),
      );

      if (response.statusCode != 200) {
        // Revert nếu API lỗi
        if (currentlyFavorite) {
          favorites.add(product);
        } else {
          favorites.removeWhere((p) => p.id == product.id);
        }
        _safeSnackbar('Lỗi', 'Không thể đồng bộ với server', isError: true);
      }
    } catch (e) {
      print("Lỗi API Wishlist: $e");
      // Revert nếu lỗi mạng
      if (currentlyFavorite) favorites.add(product);
      else favorites.removeWhere((p) => p.id == product.id);
    }
  }

  // --- HÀM HIỂN THỊ SNACKBAR AN TOÀN (FIX LỖI OVERLAY) ---
  void _safeSnackbar(String title, String message, {bool isError = false, bool isSuccess = false}) {
    // Chỉ hiện snackbar khi Get có context (tức là App đã dựng xong)
    if (Get.context != null) {
      Get.snackbar(
        title, 
        message,
        snackPosition: SnackPosition.BOTTOM,
        duration: const Duration(seconds: 1),
        backgroundColor: isError ? Colors.red.withOpacity(0.1) : (isSuccess ? Colors.green.withOpacity(0.1) : Colors.white),
        colorText: isError ? Colors.red : (isSuccess ? Colors.green : Colors.black),
        margin: const EdgeInsets.all(10),
        isDismissible: true,
      );
    } else {
      print("⚠️ Warning: App chưa sẵn sàng overlay. Không thể hiện Snackbar: $message");
    }
  }
}