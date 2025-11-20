import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter_app/shop/models/location_models.dart';
import 'package:flutter_app/shop/controllers/address_controller.dart';
import 'package:flutter_app/shop/models/address_model.dart';

class AddAddressController extends GetxController {
  final String baseUrl = "http://10.0.2.2:8000/api/address"; 
  
  var provinces = <ProvinceModel>[].obs;
  var districts = <DistrictModel>[].obs;
  var wards = <WardModel>[].obs;
  var hamlets = <HamletModel>[].obs;

  var selectedProvince = Rxn<int>();
  var selectedDistrict = Rxn<int>();
  var selectedWard = Rxn<int>();
  var selectedHamlet = Rxn<int>();

  // ✅ THÊM 2 CONTROLLER NÀY
  final nameController = TextEditingController();
  final phoneController = TextEditingController();
  final detailController = TextEditingController();
  
  final isLoading = false.obs;
  
  var isEditMode = false.obs;
  int? addressIdToEdit;

  @override
  void onInit() {
    fetchProvinces();
    super.onInit();
  }

  Future<void> initUpdateData(AddressModel address) async {
    isEditMode.value = true;
    addressIdToEdit = address.id;
    
    // ✅ ĐIỀN DỮ LIỆU CŨ VÀO FORM
    nameController.text = address.name;
    phoneController.text = address.phoneNumber;
    detailController.text = address.street;

    isLoading.value = true;
    try {
      if (provinces.isEmpty) await fetchProvinces();
      var p = provinces.firstWhereOrNull((element) => element.name == address.city);
      if (p != null) {
        selectedProvince.value = p.id;
        await fetchWards(p.id);
        var w = wards.firstWhereOrNull((element) => element.name == address.ward);
        if (w != null) {
          selectedWard.value = w.id;
          await fetchHamlets(w.id);
        }
      }
    } catch (e) {
      print("Lỗi điền dữ liệu cũ: $e");
    } finally {
      isLoading.value = false;
    }
  }

  Future<void> fetchProvinces() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/provinces/'));
      if (response.statusCode == 200) {
        final List data = json.decode(utf8.decode(response.bodyBytes));
        provinces.value = data.map((e) => ProvinceModel.fromJson(e)).toList();
      }
    } catch (e) { print('Lỗi tỉnh: $e'); }
  }
  
  Future<void> fetchWards(int provinceId) async {
    wards.clear(); hamlets.clear(); selectedWard.value = null; selectedHamlet.value = null;
    try {
      final response = await http.get(Uri.parse('$baseUrl/wards/?province_id=$provinceId'));
      if (response.statusCode == 200) {
        final List data = json.decode(utf8.decode(response.bodyBytes));
        wards.value = data.map((e) => WardModel.fromJson(e)).toList();
      }
    } catch (e) { print('Lỗi phường: $e'); }
  }

  Future<void> fetchHamlets(int wardId) async {
     hamlets.clear(); selectedHamlet.value = null;
     try {
      final response = await http.get(Uri.parse('$baseUrl/hamlets/?ward_id=$wardId'));
      if (response.statusCode == 200) {
        final List data = json.decode(utf8.decode(response.bodyBytes));
        hamlets.value = data.map((e) => HamletModel.fromJson(e)).toList();
      }
    } catch (e) { print('Lỗi thôn: $e'); }
  }

  Future<void> saveAddress() async {
    // ✅ VALIDATE THÊM NAME VÀ PHONE
    if (nameController.text.isEmpty || phoneController.text.isEmpty ||
        detailController.text.isEmpty || selectedProvince.value == null || selectedWard.value == null) {
      Get.snackbar('Thông báo', 'Vui lòng điền đầy đủ thông tin', 
         snackPosition: SnackPosition.BOTTOM, margin: const EdgeInsets.all(10));
      return;
    }

    isLoading.value = true;
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('token');

      final body = {
        // ✅ GỬI THÊM NAME VÀ PHONE LÊN SERVER
        "name": nameController.text,
        "phone": phoneController.text,
        "detail": detailController.text,
        "province": selectedProvince.value,
        "ward": selectedWard.value,
        "hamlet": selectedHamlet.value,
        "is_default": true
      };

      http.Response response;
      
      if (isEditMode.value && addressIdToEdit != null) {
        response = await http.put(
          Uri.parse('$baseUrl/my-addresses/$addressIdToEdit/'),
          headers: {'Content-Type': 'application/json', 'Authorization': 'Bearer $token'},
          body: json.encode(body),
        );
      } else {
        response = await http.post(
          Uri.parse('$baseUrl/my-addresses/'),
          headers: {'Content-Type': 'application/json', 'Authorization': 'Bearer $token'},
          body: json.encode(body),
        );
      }

      if (response.statusCode == 201 || response.statusCode == 200) {
        if (Get.context != null) {
          Navigator.of(Get.context!).pop();
        }

        Get.snackbar('Thành công', isEditMode.value ? 'Đã cập nhật địa chỉ' : 'Đã thêm địa chỉ mới',
            backgroundColor: Colors.green, colorText: Colors.white,
            snackPosition: SnackPosition.BOTTOM, margin: const EdgeInsets.all(10));
        
        if (Get.isRegistered<AddressController>()) {
          Get.find<AddressController>().fetchUserAddresses();
        }
      } else {
        Get.snackbar('Lỗi', 'Server: ${response.body}');
      }
    } catch (e) {
      Get.snackbar('Lỗi', 'Lỗi kết nối: $e');
    } finally {
      isLoading.value = false;
    }
  }
}