import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter_app/shop/models/cart_item_model.dart';
import 'package:flutter_app/shop/controllers/voucher_controller.dart';

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
    print('=== Calculating total ===');
    for (var item in cartItems) {
      print('Item ${item.itemId}: selected=${item.isSelected.value}, qty=${item.quantity}, price=${item.price}, subTotal=${item.subTotal}');
      if (item.isSelected.value) {
        // Ưu tiên dùng subTotal backend tính sẵn, nếu không thì tự nhân
        final itemTotal = (item.subTotal > 0) ? item.subTotal : (item.price * item.quantity);
        print('  -> Adding $itemTotal to total');
        total += itemTotal;
      }
    }
    print('Total amount: $total');
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
        WidgetsBinding.instance.addPostFrameCallback((_) {
          Get.snackbar('Lỗi', 'Vui lòng đăng nhập');
        });
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
        fetchCart();
        // Đợi frame tiếp theo để đảm bảo overlay đã sẵn sàng
        WidgetsBinding.instance.addPostFrameCallback((_) {
          Get.snackbar('Thành công', 'Đã thêm vào giỏ hàng', 
            snackPosition: SnackPosition.BOTTOM);
        });
      } else {
        var msg = json.decode(response.body)['error'] ?? 'Lỗi không xác định';
        // Schedule snackbar sau frame
        WidgetsBinding.instance.addPostFrameCallback((_) {
          Get.snackbar('Lỗi', msg);
        });
      }
    } catch (e) {
      print(e);
    }
  }

  // Debounce map để tránh gọi API quá nhanh
  final _debounceTimers = <int, Timer?>{};

  Future<void> updateQuantity(int itemId, int newQuantity) async {
    // Optimistic update
    final index = cartItems.indexWhere((item) => item.itemId == itemId);
    if (index != -1) {
      cartItems[index].quantity = newQuantity;
      cartItems.refresh(); 
      updateCartTotal(); 
    }

    // Hủy timer cũ nếu đang chạy
    _debounceTimers[itemId]?.cancel();
    
    // Tạo timer mới: chỉ gọi API sau 500ms không có thay đổi
    _debounceTimers[itemId] = Timer(const Duration(milliseconds: 500), () async {
      try {
        final prefs = await SharedPreferences.getInstance();
        final token = prefs.getString('token');
        
        print('Updating cart item $itemId to quantity: $newQuantity');
        
        final response = await http.patch(
          Uri.parse('$baseUrl/$itemId/update_quantity/'),
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer $token'
          },
          body: json.encode({'quantity': newQuantity}),
        );
        
        if (response.statusCode != 200) {
          print('Update failed: ${response.statusCode} - ${response.body}');
          
          // Hiển thị lỗi từ backend
          try {
            final errorData = json.decode(response.body);
            final errorMsg = errorData['error'] ?? 'Lỗi không xác định';
            WidgetsBinding.instance.addPostFrameCallback((_) {
              Get.snackbar('Lỗi', errorMsg,
                snackPosition: SnackPosition.BOTTOM,
                backgroundColor: Colors.red,
                colorText: Colors.white,
              );
            });
          } catch (e) {
            print('Error parsing error response: $e');
          }
          
          fetchCart(); // Revert on error
        } else {
          print('Update success: ${response.body}');
          
          // Parse response và sync lại cart từ server
          final data = json.decode(utf8.decode(response.bodyBytes));
          if (data['items'] != null) {
            final serverItems = data['items'] as List;
            
            // Tạo map từ server items để dễ lookup
            final serverItemsMap = <int, Map<String, dynamic>>{};
            for (var item in serverItems) {
              serverItemsMap[item['item_id']] = item;
            }
            
            // Update từng item hiện tại với data từ server (giữ nguyên thứ tự)
            for (int i = 0; i < cartItems.length; i++) {
              final currentItemId = cartItems[i].itemId;
              
              if (serverItemsMap.containsKey(currentItemId)) {
                // Lưu selection state cũ
                final oldSelection = cartItems[i].isSelected.value;
                
                // Thay thế item với data mới từ server
                cartItems[i] = CartItemModel.fromJson(serverItemsMap[currentItemId]!);
                
                // Khôi phục selection
                cartItems[i].isSelected.value = oldSelection;
                
                // Remove khỏi map để track items đã xử lý
                serverItemsMap.remove(currentItemId);
              }
            }
            
            // Thêm các items mới từ server (nếu có - ví dụ user add từ device khác)
            if (serverItemsMap.isNotEmpty) {
              for (var newItem in serverItemsMap.values) {
                cartItems.add(CartItemModel.fromJson(newItem));
              }
            }
            
            // Refresh UI và tính lại total
            cartItems.refresh();
            updateCartTotal();
          }
        }
      } catch (e) {
        print("Lỗi update: $e");
        fetchCart(); // Revert
      }
    });
    // If user changes cart, release any voucher reservations
    try {
      if (Get.isRegistered<VoucherController>()) {
        final vc = Get.find<VoucherController>();
        vc.releaseAllReservations();
      }
    } catch (e) {}
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
      
      WidgetsBinding.instance.addPostFrameCallback((_) {
        Get.snackbar('Thành công', 'Đã xóa sản phẩm');
      });
    } catch (e) {
      print("Lỗi xóa: $e");
      fetchCart();
    }
  }
}