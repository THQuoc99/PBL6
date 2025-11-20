import 'dart:convert';
import 'package:get/get.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter_app/shop/models/product_model.dart';
import 'package:flutter_app/shop/controllers/user_controller.dart';

class WishlistController extends GetxController {
  static WishlistController get instance => Get.find();

  // Danh sách yêu thích (Reactive)
  final RxList<ProductModel> favorites = <ProductModel>[].obs;
  
  // Lấy UserController để biết ai đang đăng nhập
  final userController = Get.find<UserController>();

  @override
  void onInit() {
    super.onInit();
    // 1. Tải danh sách lần đầu
    loadFavorites();
    
    // 2. ✅ TỰ ĐỘNG: Lắng nghe sự thay đổi của UserID
    // Khi User đăng nhập hoặc đăng xuất -> UserID đổi -> Tự động tải lại wishlist của người đó
    // (Đảm bảo UserController có biến userID là RxString hoặc RxInt)
    ever(userController.userID, (_) {
      print("🔄 User changed to ${userController.userID.value}, reloading wishlist...");
      loadFavorites();
    });
  }

  // ✅ Tạo Key lưu trữ động theo User ID
  // Ví dụ: 'wishlist_1', 'wishlist_2', 'wishlist_guest'
  String get _storageKey {
    final uid = userController.userID.value.toString();
    if (uid.isEmpty || uid == '0') {
      return 'wishlist_guest'; // Key cho khách chưa đăng nhập
    }
    return 'wishlist_$uid'; // Key riêng cho từng user
  }

  // Thêm/Xóa sản phẩm
  void toggleFavorite(ProductModel product) {
    if (isFavorite(product.id)) {
      favorites.removeWhere((p) => p.id == product.id);
      Get.snackbar('Đã xóa', 'Đã xóa khỏi danh sách yêu thích', 
        snackPosition: SnackPosition.BOTTOM, duration: const Duration(milliseconds: 800));
    } else {
      favorites.add(product);
      Get.snackbar('Đã thêm', 'Đã thêm vào danh sách yêu thích',
        snackPosition: SnackPosition.BOTTOM, duration: const Duration(milliseconds: 800));
    }
    saveFavorites();
  }

  bool isFavorite(int productId) {
    return favorites.any((p) => p.id == productId);
  }

  Future<void> saveFavorites() async {
    final prefs = await SharedPreferences.getInstance();
    final List<String> jsonList = favorites.map((item) => jsonEncode(item.toJson())).toList();
    
    // ✅ Lưu vào Key riêng của user hiện tại
    print("💾 Saving wishlist to key: $_storageKey");
    await prefs.setStringList(_storageKey, jsonList);
  }

  Future<void> loadFavorites() async {
    final prefs = await SharedPreferences.getInstance();
    
    // ✅ Đọc từ Key riêng của user hiện tại
    print("📂 Loading wishlist from key: $_storageKey");
    final List<String>? jsonList = prefs.getStringList(_storageKey);
    
    if (jsonList != null) {
      favorites.assignAll(
        jsonList.map((item) => ProductModel.fromJson(jsonDecode(item))).toList()
      );
    } else {
      // Nếu key này chưa có dữ liệu (user mới), làm rỗng list
      favorites.clear();
    }
  }
}