import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter_app/shop/models/address_model.dart';

class AddressController extends GetxController {
  static AddressController get instance => Get.find();

  final isLoading = false.obs;
  final addresses = <AddressModel>[].obs;
  final selectedAddress = Rx<AddressModel?>(null);

  final String baseUrl = "http://10.0.2.2:8000/api/address";

  @override
  void onInit() {
    fetchUserAddresses();
    super.onInit();
  }

  Future<void> fetchUserAddresses() async {
    try {
      isLoading.value = true;
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('token');
      
      if (token == null) return;

      final url = Uri.parse('$baseUrl/my-addresses/');
      final response = await http.get(
        url,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(utf8.decode(response.bodyBytes));
        addresses.value = data.map((e) => AddressModel.fromJson(e)).toList();
        
        if (addresses.isNotEmpty && selectedAddress.value == null) {
          var defaultAddr = addresses.firstWhereOrNull((element) => element.isDefault);
          selectedAddress.value = defaultAddr ?? addresses.first;
        }
      }
    } catch (e) {
      print("❌ Lỗi: $e");
    } finally {
      isLoading.value = false;
    }
  }

  void selectAddress(AddressModel address) {
    selectedAddress.value = address;
  }

  // ✅ HÀM XÓA ĐỊA CHỈ (ĐÃ FIX LỖI CRASH)
  Future<void> deleteAddress(int addressId) async {
    Get.defaultDialog(
      title: "Xóa địa chỉ",
      middleText: "Bạn có chắc chắn muốn xóa địa chỉ này không?",
      textConfirm: "Xóa",
      textCancel: "Hủy",
      confirmTextColor: Colors.white,
      buttonColor: Colors.red,
      onConfirm: () async {
        // ⚠️ THAY ĐỔI QUAN TRỌNG: Dùng Navigator để đóng Dialog an toàn
        // Get.back() gây xung đột với SnackbarController
        Navigator.of(Get.overlayContext!).pop(); 
        
        isLoading.value = true;
        
        try {
          final prefs = await SharedPreferences.getInstance();
          final token = prefs.getString('token');

          final url = Uri.parse('$baseUrl/my-addresses/$addressId/');
          final response = await http.delete(
            url,
            headers: {'Authorization': 'Bearer $token'},
          );

          if (response.statusCode == 204) {
            await fetchUserAddresses();
            Get.snackbar(
              'Thành công', 
              'Đã xóa địa chỉ', 
              backgroundColor: Colors.green, 
              colorText: Colors.white, 
              snackPosition: SnackPosition.BOTTOM,
              margin: const EdgeInsets.all(10)
            );
          } else {
             Get.snackbar('Lỗi', 'Không xóa được: ${response.statusCode}', backgroundColor: Colors.red, colorText: Colors.white);
          }
        } catch (e) {
          print("Lỗi xóa: $e");
        } finally {
          isLoading.value = false;
        }
      }
    );
  }
}