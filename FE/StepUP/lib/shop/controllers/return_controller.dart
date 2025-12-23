import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter_app/shop/models/return_model.dart';
import 'package:flutter_app/shop/models/order_model.dart';

class ReturnController extends GetxController {
  static ReturnController get instance => Get.find();

  final isLoading = false.obs;
  final returns = <ReturnRequestModel>[].obs;
  final selectedReturn = Rxn<ReturnRequestModel>();
  final selectedFilterStatus = Rxn<String>(); // null = all, 'pending', 'approved', etc.
  
  // Form fields
  final selectedReason = 'damaged'.obs;
  final descriptionController = TextEditingController();
  final trackingCodeController = TextEditingController();
  final selectedImages = <File>[].obs;
  final selectedItems = <OrderItemModel>[].obs;
  final itemQuantities = <int, int>{}.obs; // orderItemId -> quantity

  final String baseUrl = "http://10.0.2.2:8000/api/returns";

  final reasonOptions = const {
    'wrong_item': 'Giao sai sản phẩm',
    'damaged': 'Hàng bị hỏng/lỗi',
    'not_as_described': 'Không đúng mô tả',
    'size_issue': 'Không vừa size',
    'changed_mind': 'Đổi ý không muốn mua',
    'quality_issue': 'Chất lượng kém',
    'other': 'Lý do khác',
  };

  @override
  void onClose() {
    descriptionController.dispose();
    trackingCodeController.dispose();
    super.onClose();
  }

  /// Fetch danh sách return requests của user
  Future<void> fetchMyReturns() async {
    try {
      isLoading.value = true;
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('token');

      if (token == null) {
        throw 'Vui lòng đăng nhập';
      }

      final response = await http.get(
        Uri.parse(baseUrl),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        final data = json.decode(utf8.decode(response.bodyBytes));
        final List returnsList = data is List ? data : (data['results'] ?? data['data'] ?? []);
        
        returns.value = returnsList
            .map((json) => ReturnRequestModel.fromJson(json))
            .toList();
      } else {
        throw 'Không thể tải danh sách yêu cầu trả hàng';
      }
    } catch (e) {
      print('Error fetchMyReturns: $e');
    } finally {
      isLoading.value = false;
    }
  }

  /// Fetch chi tiết return request
  Future<void> fetchReturnDetail(int returnId) async {
    try {
      isLoading.value = true;
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('token');

      if (token == null) {
        throw 'Vui lòng đăng nhập';
      }

      final response = await http.get(
        Uri.parse('$baseUrl/$returnId/'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        final data = json.decode(utf8.decode(response.bodyBytes));
        selectedReturn.value = ReturnRequestModel.fromJson(data);
      } else {
        throw 'Không thể tải chi tiết yêu cầu';
      }
    } catch (e) {
      print('Error fetchReturnDetail: $e');
    } finally {
      isLoading.value = false;
    }
  }

  /// Tạo return request mới
  Future<bool> createReturnRequest({
    required int orderId,
    int? subOrderId,
    String returnType = 'refund',
  }) async {
    try {
      // Validation checks
      if (selectedItems.isEmpty) {
        print('Validation error: No items selected');
        return false;
      }

      if (descriptionController.text.trim().isEmpty) {
        print('Validation error: No description');
        return false;
      }

      // Nếu damaged hoặc not_as_described, bắt buộc phải có ảnh
      if ((selectedReason.value == 'damaged' || selectedReason.value == 'not_as_described') 
          && selectedImages.isEmpty) {
        print('Validation error: Photos required for damaged/not_as_described');
        return false;
      }

      isLoading.value = true;
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('token');

      if (token == null) {
        throw 'Vui lòng đăng nhập';
      }

      // Prepare multipart request
      var request = http.MultipartRequest('POST', Uri.parse('$baseUrl/create_return/'));
      request.headers['Authorization'] = 'Bearer $token';

      // Add fields
      request.fields['order_id'] = orderId.toString();
      if (subOrderId != null) {
        request.fields['sub_order_id'] = subOrderId.toString();
      }
      request.fields['return_type'] = returnType;
      request.fields['reason'] = selectedReason.value;
      request.fields['description'] = descriptionController.text.trim();

      // Add items as JSON string
      final items = selectedItems.map((item) {
        return {
          'order_item_id': item.itemId,
          'quantity': itemQuantities[item.itemId] ?? item.quantity,
        };
      }).toList();
      request.fields['items'] = json.encode(items);

      // Add images
      for (var image in selectedImages) {
        request.files.add(await http.MultipartFile.fromPath('images', image.path));
      }

      print('Sending request to: $baseUrl/create_return/');
      print('Request fields: ${request.fields}');
      print('Request files: ${request.files.length} images');

      final streamedResponse = await request.send();
      final response = await http.Response.fromStream(streamedResponse);

      print('Response status: ${response.statusCode}');
      print('Response body: ${response.body}');

      if (response.statusCode == 201 || response.statusCode == 200) {
        print('✅ Return request created successfully');
        
        // Reset form
        clearForm();
        
        // Refresh list
        await fetchMyReturns();
        
        return true;
      } else {
        final error = json.decode(response.body);
        final errorMsg = error['error'] ?? error['detail'] ?? 'Không thể tạo yêu cầu trả hàng';
        print('API Error: $errorMsg');
        throw errorMsg;
      }
    } catch (e) {
      print('Exception caught: $e');
      // Don't show snackbar here to avoid overlay crash
      // Error will be shown in UI via return false
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  /// Upload ảnh từ camera hoặc gallery
  Future<void> pickImage({required ImageSource source}) async {
    try {
      final picker = ImagePicker();
      final pickedFile = await picker.pickImage(
        source: source,
        maxWidth: 1920,
        maxHeight: 1080,
        imageQuality: 85,
      );

      if (pickedFile != null) {
        selectedImages.add(File(pickedFile.path));
      }
    } catch (e) {
      print('Error picking image: $e');
    }
  }

  /// Xóa ảnh
  void removeImage(int index) {
    if (index >= 0 && index < selectedImages.length) {
      selectedImages.removeAt(index);
    }
  }

  /// Toggle chọn item
  void toggleItem(OrderItemModel item) {
    if (selectedItems.contains(item)) {
      selectedItems.remove(item);
      itemQuantities.remove(item.itemId);
    } else {
      selectedItems.add(item);
      itemQuantities[item.itemId] = item.quantity; // Default full quantity
    }
  }

  /// Update số lượng trả cho item
  void updateItemQuantity(int itemId, int quantity) {
    itemQuantities[itemId] = quantity;
  }

  /// Cancel return request
  Future<bool> cancelReturn(int returnId) async {
    try {
      isLoading.value = true;
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('token');

      if (token == null) {
        throw 'Vui lòng đăng nhập';
      }

      final response = await http.post(
        Uri.parse('$baseUrl/$returnId/cancel/'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        print('✅ Return cancelled successfully');
        
        await fetchMyReturns();
        return true;
      } else {
        final error = json.decode(response.body);
        throw error['error'] ?? 'Không thể hủy yêu cầu';
      }
    } catch (e) {
      print('Error cancelReturn: $e');
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  /// Update tracking code
  Future<bool> updateTrackingCode(int returnId, String trackingCode) async {
    try {
      if (trackingCode.trim().isEmpty) {
        throw 'Vui lòng nhập mã vận đơn';
      }

      isLoading.value = true;
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('token');

      if (token == null) {
        throw 'Vui lòng đăng nhập';
      }

      final response = await http.post(
        Uri.parse('$baseUrl/$returnId/update_tracking/'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
        body: json.encode({
          'tracking_code': trackingCode.trim(),
        }),
      );

      if (response.statusCode == 200) {
        print('✅ Tracking code updated successfully');
        
        await fetchReturnDetail(returnId);
        return true;
      } else {
        final error = json.decode(response.body);
        throw error['error'] ?? 'Không thể cập nhật mã vận đơn';
      }
    } catch (e) {
      print('Error updateTrackingCode: $e');
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  /// Clear form data
  void clearForm() {
    selectedReason.value = 'damaged';
    descriptionController.clear();
    trackingCodeController.clear();
    selectedImages.clear();
    selectedItems.clear();
    itemQuantities.clear();
  }

  /// Filter returns by status
  List<ReturnRequestModel> get filteredReturns {
    if (selectedFilterStatus.value == null) {
      return returns;
    }
    return returns.where((r) => r.status == selectedFilterStatus.value).toList();
  }

  /// Set filter status
  void setFilterStatus(String? status) {
    selectedFilterStatus.value = status;
  }
}
