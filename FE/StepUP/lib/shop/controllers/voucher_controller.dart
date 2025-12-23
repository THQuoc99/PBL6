import 'dart:convert';
import 'package:get/get.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../models/voucher_model.dart';

class VoucherController extends GetxController {
  static VoucherController get instance => Get.find();

  // --- DATA SOURCES ---
  final allVouchers = <VoucherModel>[].obs;
  final myWalletVouchers = <VoucherModel>[].obs; 
  
  final availableStoreVouchers = <VoucherModel>[].obs;
  final availablePlatformVouchers = <VoucherModel>[].obs;
  final availableShippingVouchers = <VoucherModel>[].obs;
  
  final isLoading = false.obs;

  // --- SELECTIONS ---
  final selectedStoreVouchers = <String, VoucherModel>{}.obs;
  final selectedPlatformVoucher = Rxn<VoucherModel>();
  final selectedShippingVoucher = Rxn<VoucherModel>();

  final String baseUrl = 'http://10.0.2.2:8000/api/discounts';

  @override
  void onInit() {
    super.onInit();
    fetchAllVouchers();
    fetchMyWallet();
  }

  // Lấy tất cả voucher cho trang Kho Voucher
  Future<void> fetchAllVouchers() async {
    try {
      isLoading.value = true;
      final response = await http.get(Uri.parse('$baseUrl/'));
      if (response.statusCode == 200) {
        final List<dynamic> data = jsonDecode(utf8.decode(response.bodyBytes));
        allVouchers.assignAll(data.map((e) => VoucherModel.fromJson(e)).toList());
      }
    } catch (e) {
      print('Error fetching all vouchers: $e');
    } finally {
      isLoading.value = false;
    }
  }

  Future<void> fetchMyWallet() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('token');
      if (token == null) return;

      final response = await http.get(
        Uri.parse('$baseUrl/my-wallet/'),
        headers: {'Authorization': 'Bearer $token'},
      );

      if (response.statusCode == 200) {
        final List<dynamic> data = jsonDecode(utf8.decode(response.bodyBytes));
        myWalletVouchers.assignAll(data.map((e) {
          return VoucherModel.fromJson(e['voucher'] ?? e);
        }).toList());
      }
    } catch (e) {
      print('Error fetching wallet: $e');
    }
  }

  // --- [FIX] API Lấy voucher khả dụng (Dùng String Store ID) ---
  Future<void> fetchAvailableVouchers({
    required List<String> storeIds, 
    required double totalOrderAmount
  }) async {
    try {
      isLoading.value = true;
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('token');

      final body = {
        "store_ids": storeIds,
        "total_amount": totalOrderAmount
      };

      print("📤 Fetching available vouchers with: $body");

      final response = await http.post(
        Uri.parse('$baseUrl/available/'),
        headers: {
          'Content-Type': 'application/json',
          if (token != null) 'Authorization': 'Bearer $token',
        },
        body: jsonEncode(body),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(utf8.decode(response.bodyBytes));
        
        availableStoreVouchers.assignAll((data['store_vouchers'] as List)
            .map((e) => VoucherModel.fromJson(e)).toList());
            
        availablePlatformVouchers.assignAll((data['platform_vouchers'] as List)
            .map((e) => VoucherModel.fromJson(e)).toList());
            
        availableShippingVouchers.assignAll((data['shipping_vouchers'] as List)
            .map((e) => VoucherModel.fromJson(e)).toList());
            
        _autoSelectBestVouchers(storeIds);
      } else {
        print("❌ Server Error (${response.statusCode}): ${response.body}");
      }
    } catch (e) {
      print('❌ Error fetching available vouchers: $e');
    } finally {
      isLoading.value = false;
    }
  }

  // --- [FIX] Auto select với String Store ID ---
  void _autoSelectBestVouchers(List<String> storeIds) {
    for (var storeId in storeIds) {
      // Chỉ chọn nếu chưa có voucher nào được chọn cho shop này
      if (!selectedStoreVouchers.containsKey(storeId)) {
        var best = availableStoreVouchers
            .where((v) {
                // So sánh Store ID (Chuyển hết về String để so sánh an toàn)
                String vStoreId = v.storeId?.toString() ?? '';
                return vStoreId == storeId && v.isUsable && v.isSaved;
            })
            .fold<VoucherModel?>(null, (curr, next) {
              if (curr == null) return next;
              return next.discountValue > curr.discountValue ? next : curr;
            });
            
        if (best != null) {
          // Lưu vào map với Key là storeId từ giỏ hàng
          selectedStoreVouchers[storeId] = best;
        }
      }
    }

    // 2. Auto Platform Voucher
    if (selectedPlatformVoucher.value == null) {
       var best = availablePlatformVouchers
            .where((v) => v.isUsable && v.isSaved)
            .fold<VoucherModel?>(null, (curr, next) {
              if (curr == null) return next;
              return next.discountValue > curr.discountValue ? next : curr;
            });
       if (best != null) selectedPlatformVoucher.value = best;
    }

    // 3. Auto Shipping Voucher
    if (selectedShippingVoucher.value == null) {
       var best = availableShippingVouchers
            .where((v) => v.isUsable && v.isSaved)
            .fold<VoucherModel?>(null, (curr, next) {
              if (curr == null) return next;
              if (next.isFreeShipping && !curr.isFreeShipping) return next;
              if (!next.isFreeShipping && curr.isFreeShipping) return curr;
              return next.discountValue > curr.discountValue ? next : curr;
            });
       if (best != null) selectedShippingVoucher.value = best;
    }
  }

  void selectStoreVoucher(String storeId, VoucherModel? voucher) {
    if (voucher == null) {
      // Bỏ chọn: Xóa khỏi map
      selectedStoreVouchers.remove(storeId);
    } else {
      // Chọn mới: Ghi đè vào map với key là storeId
      selectedStoreVouchers[storeId] = voucher;
    }
    
    // Cập nhật UI ngay lập tức
    selectedStoreVouchers.refresh();
    update(); // Force update các widget lắng nghe
  }

  void selectPlatformVoucher(VoucherModel? voucher) {
    selectedPlatformVoucher.value = voucher;
  }

  void selectShippingVoucher(VoucherModel? voucher) {
    selectedShippingVoucher.value = voucher;
  }

  Map<String, String> getVouchersForOrder() {
    final Map<String, String> map = {};
    selectedStoreVouchers.forEach((storeId, voucher) {
      map[storeId] = voucher.code;
    });
    if (selectedPlatformVoucher.value != null) {
      map['platform'] = selectedPlatformVoucher.value!.code;
    }
    if (selectedShippingVoucher.value != null) {
      map['shipping'] = selectedShippingVoucher.value!.code;
    }
    return map;
  }

  Future<bool> saveVoucher(String code) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('token');
      if (token == null) return false;
      
      final response = await http.post(
        Uri.parse('$baseUrl/save/'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: jsonEncode({'code': code})
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        fetchMyWallet();
        fetchAllVouchers(); 
        return true;
      }
      return false;
    } catch (e) {
      return false;
    }
  }

  Future<void> releaseAllReservations() async {
     selectedStoreVouchers.clear();
     selectedPlatformVoucher.value = null;
     selectedShippingVoucher.value = null;
  }
}