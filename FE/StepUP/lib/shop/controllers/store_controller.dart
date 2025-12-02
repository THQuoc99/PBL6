import 'dart:convert';
import 'package:get/get.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart'; // Import thêm cái này
import 'package:flutter_app/shop/models/product_model.dart';
import 'package:flutter_app/shop/models/store_model.dart';

class StoreController extends GetxController {
  final String baseUrl = "http://10.0.2.2:8000/api"; 
  
  final isLoading = false.obs;
  final store = Rxn<Store>();
  final storeProducts = <ProductModel>[].obs;

  // Biến observable để theo dõi trạng thái follow realtime trên UI
  final isFollowing = false.obs; 
  final followerCount = 0.obs;

  Future<void> fetchStoreData(String storeId) async {
    isLoading.value = true;
    try {
      // Lấy Token để Backend biết ai đang xem (để check is_following)
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('token');
      Map<String, String> headers = {};
      if (token != null) headers['Authorization'] = 'Bearer $token';

      // 1. Lấy thông tin Store
      final storeResponse = await http.get(
        Uri.parse('$baseUrl/store/$storeId/'),
        headers: headers
      );
      
      if (storeResponse.statusCode == 200) {
        final data = json.decode(utf8.decode(storeResponse.bodyBytes));
        final storeData = Store.fromJson(data);
        store.value = storeData;
        
        // Cập nhật các biến trạng thái UI
        isFollowing.value = storeData.isFollowing;
        followerCount.value = storeData.followersCount;
      }

      // 2. Lấy sản phẩm (giữ nguyên)
      final productsResponse = await http.get(Uri.parse('$baseUrl/products/?store_id=$storeId'));
      if (productsResponse.statusCode == 200) {
        final List listData = json.decode(utf8.decode(productsResponse.bodyBytes));
        storeProducts.value = listData.map((e) => ProductModel.fromJson(e)).toList();
      }
      
    } catch (e) {
      print("❌ Lỗi tải Store: $e");
    } finally {
      isLoading.value = false;
    }
  }

  // ✅ HÀM FOLLOW/UNFOLLOW
  Future<void> followStore(String storeId) async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('token');

    if (token == null) {
      Get.snackbar('Thông báo', 'Vui lòng đăng nhập để theo dõi shop');
      return;
    }

    // --- Optimistic Update (Cập nhật UI giả lập ngay lập tức) ---
    final bool previousState = isFollowing.value;
    isFollowing.value = !previousState; // Đảo trạng thái
    if (isFollowing.value) {
      followerCount.value++;
    } else {
      followerCount.value--;
    }

    try {
      // Gọi API
      final response = await http.post(
        Uri.parse('$baseUrl/store/$storeId/follow/'),
        headers: {'Authorization': 'Bearer $token'},
      );

      if (response.statusCode != 200) {
        // Nếu API lỗi -> Revert lại trạng thái cũ
        isFollowing.value = previousState;
        followerCount.value = previousState ? followerCount.value + 1 : followerCount.value - 1;
        Get.snackbar('Lỗi', 'Không thể thực hiện thao tác');
      }
    } catch (e) {
      print("Lỗi Follow: $e");
      // Revert lại nếu lỗi mạng
      isFollowing.value = previousState;
      followerCount.value = previousState ? followerCount.value + 1 : followerCount.value - 1;
    }
  }
}