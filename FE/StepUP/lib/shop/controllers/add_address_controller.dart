import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter_app/shop/models/location_models.dart';
import 'package:flutter_app/shop/controllers/address_controller.dart';
import 'package:flutter_app/shop/models/address_model.dart';

class AddAddressController extends GetxController {
  final String locationApiUrl = "https://provinces.open-api.vn/api"; 
  final String backendUrl = "http://10.0.2.2:8000/api/address";

  var provinces = <ProvinceModel>[].obs;
  var districts = <DistrictModel>[].obs;
  var wards = <WardModel>[].obs;

  var selectedProvince = Rxn<ProvinceModel>();
  var selectedDistrict = Rxn<DistrictModel>();
  var selectedWard = Rxn<WardModel>();

  final nameController = TextEditingController();
  final phoneController = TextEditingController();
  final detailController = TextEditingController();
  
  final isLoading = false.obs;
  var isEditMode = false.obs;
  int? addressIdToEdit;

  @override
  void onInit() {
    super.onInit();
    // Tải danh sách tỉnh ngay khi mở màn hình
    fetchProvinces();
  }

  // --- LOGIC KHÔI PHỤC DỮ LIỆU KHI SỬA (QUAN TRỌNG) ---
  Future<void> initUpdateData(AddressModel address) async {
    isEditMode.value = true;
    addressIdToEdit = address.id;
    
    // 1. Điền text cơ bản
    nameController.text = address.name;
    phoneController.text = address.phoneNumber;
    detailController.text = address.detail;

    // 2. Khôi phục Dropdown (Phức tạp vì phải đợi API load xong mới chọn được)
    // Đảm bảo danh sách tỉnh đã có
    if (provinces.isEmpty) {
      await fetchProvinces();
    }

    // A. Tìm và chọn Tỉnh
    // So sánh tên từ DB (address.province) với tên trong list API
    // Lưu ý: Cần chuẩn hóa chuỗi nếu cần (trim, toLowerCase) để so sánh chính xác
    var foundProvince = provinces.firstWhereOrNull(
      (p) => p.name.toLowerCase().contains(address.province.toLowerCase()) 
          || address.province.toLowerCase().contains(p.name.toLowerCase())
    );

    if (foundProvince != null) {
      selectedProvince.value = foundProvince;
      
      // B. Tải danh sách Huyện của Tỉnh đó
      await fetchDistricts(foundProvince.id);

      // C. Tìm và chọn Huyện (address.hamlet chứa tên huyện trong DB của bạn)
      var foundDistrict = districts.firstWhereOrNull(
        (d) => d.name.toLowerCase().contains(address.hamlet.toLowerCase())
            || address.hamlet.toLowerCase().contains(d.name.toLowerCase())
      );

      if (foundDistrict != null) {
        selectedDistrict.value = foundDistrict;

        // D. Tải danh sách Xã của Huyện đó
        await fetchWards(foundDistrict.id);

        // E. Tìm và chọn Xã
        var foundWard = wards.firstWhereOrNull(
          (w) => w.name.toLowerCase().contains(address.ward.toLowerCase())
              || address.ward.toLowerCase().contains(w.name.toLowerCase())
        );

        if (foundWard != null) {
          selectedWard.value = foundWard;
        }
      }
    }
  }

  Future<void> fetchProvinces() async {
    try {
      final response = await http.get(Uri.parse('$locationApiUrl/p/'));
      if (response.statusCode == 200) {
        final List data = json.decode(utf8.decode(response.bodyBytes));
        provinces.value = data.map((e) => ProvinceModel.fromJson(e)).toList();
      }
    } catch (e) {
      print('❌ Lỗi lấy Tỉnh: $e');
    }
  }
  
  Future<void> fetchDistricts(int provinceId) async {
    try {
      final response = await http.get(Uri.parse('$locationApiUrl/p/$provinceId?depth=2'));
      if (response.statusCode == 200) {
        var data = json.decode(utf8.decode(response.bodyBytes));
        var list = data['districts'] as List;
        districts.value = list.map((e) => DistrictModel.fromJson(e)).toList();
      }
    } catch (e) {
      print('❌ Lỗi Exception Huyện: $e');
    }
  }

  Future<void> fetchWards(int districtId) async {
     try {
      final response = await http.get(Uri.parse('$locationApiUrl/d/$districtId?depth=2'));
      if (response.statusCode == 200) {
        var data = json.decode(utf8.decode(response.bodyBytes));
        var list = data['wards'] as List;
        wards.value = list.map((e) => WardModel.fromJson(e)).toList();
      }
    } catch (e) {
      print('❌ Lỗi Exception Xã: $e');
    }
  }

  Future<void> saveAddress() async {
    if (nameController.text.isEmpty || phoneController.text.isEmpty ||
        detailController.text.isEmpty || selectedProvince.value == null || selectedWard.value == null) {
      Get.snackbar('Thiếu thông tin', 'Vui lòng điền đầy đủ các trường', backgroundColor: Colors.orange.withOpacity(0.2));
      return;
    }

    isLoading.value = true;
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('token');

      final body = {
        "name": nameController.text,
        "phone": phoneController.text,
        "detail": detailController.text,
        "province": selectedProvince.value!.name, 
        "ward": selectedWard.value!.name,
        "hamlet": selectedDistrict.value?.name ?? '', 
        "is_default": true
      };

      http.Response response;
      final headers = {
        'Content-Type': 'application/json', 
        'Authorization': 'Bearer $token'
      };

      if (isEditMode.value && addressIdToEdit != null) {
        response = await http.put(
          Uri.parse('$backendUrl/my-addresses/$addressIdToEdit/'),
          headers: headers, body: json.encode(body),
        );
      } else {
        response = await http.post(
          Uri.parse('$backendUrl/my-addresses/'),
          headers: headers, body: json.encode(body),
        );
      }

      if (response.statusCode == 201 || response.statusCode == 200) {
        // 1. Refresh list bên ngoài
        if (Get.isRegistered<AddressController>()) {
          await Get.find<AddressController>().fetchUserAddresses();
        }

        // 2. Đóng màn hình
        Get.back();

        // 3. Hiện thông báo
        Get.snackbar(
          'Thành công', 
          'Đã lưu địa chỉ', 
          backgroundColor: Colors.green.withOpacity(0.2),
          colorText: Colors.green,
          icon: const Icon(Icons.check_circle, color: Colors.green),
        );
      } else {
        Get.snackbar('Lỗi', 'Server trả về: ${response.body}');
      }
    } catch (e) {
      Get.snackbar('Lỗi', 'Lỗi kết nối: $e');
    } finally {
      isLoading.value = false;
    }
  }
}