import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:app_links/app_links.dart';
import 'package:flutter_app/shop/controllers/cart_controller.dart';
import 'package:flutter_app/shop/controllers/voucher_controller.dart';
import 'package:flutter_app/shop/controllers/address_controller.dart';
import 'package:flutter_app/shop/controllers/shipping_controller.dart';
import 'package:flutter_app/shop/controllers/order_list_controller.dart'; 
import 'package:flutter_app/common/widgets/success_screen/success_screen.dart';
import 'package:flutter_app/constants/image_string.dart';
import 'package:flutter_app/navigation_menu.dart';
import 'package:flutter_app/shop/models/order_model.dart';

class OrderController extends GetxController {
  static OrderController get instance => Get.find();

  late final CartController cartController;
  late final AddressController addressController;
  late final VoucherController voucherController; // Thêm voucher controller
  late final ShippingController shippingController; // Thêm shipping controller

  late AppLinks _appLinks;
  StreamSubscription<Uri>? _linkSubscription;

  final isLoading = false.obs;
  final selectedPaymentMethod = 'VNPAY'.obs;
  final noteController = TextEditingController();

  // Base URL API
  final String baseUrl = "http://10.0.2.2:8000/api/orders";
  // Root URL cho Payment (cắt bỏ phần /api/orders)
  String get rootUrl => "http://10.0.2.2:8000"; 

  @override
  void onInit() {
    super.onInit();
    cartController = Get.put(CartController());
    addressController = Get.put(AddressController());
    // Khởi tạo các controller khác nếu chưa có
    if (Get.isRegistered<VoucherController>()) {
      voucherController = Get.find<VoucherController>();
    } else {
      voucherController = Get.put(VoucherController());
    }
    
    if (Get.isRegistered<ShippingController>()) {
      shippingController = Get.find<ShippingController>();
    } else {
      shippingController = Get.put(ShippingController());
    }

    _initDeepLinkListener();
  }

  @override
  void onClose() {
    _linkSubscription?.cancel();
    noteController.dispose();
    super.onClose();
  }

  void _initDeepLinkListener() {
    _appLinks = AppLinks();
    _linkSubscription = _appLinks.uriLinkStream.listen((Uri? uri) {
      if (uri != null) {
        print("🔗 Nhận Deep Link: $uri");
        _handlePaymentResult(uri);
      }
    }, onError: (err) {
      print("Lỗi Deep Link: $err");
    });
  }

  void _handlePaymentResult(Uri uri) {
    // Xử lý deep link trả về từ VNPAY/PayPal
    String status = uri.queryParameters['status'] ?? '';
    String vnpResponseCode = uri.queryParameters['vnp_ResponseCode'] ?? '';

    // Logic kiểm tra thành công
    if (status == 'success' || vnpResponseCode == '00') {
      Get.offAll(() => SuccessScreen(
            image: AppImages.checkoutsuccess,
            title: 'Thanh toán thành công!',
            subTitle: 'Đơn hàng của bạn đã được xác nhận và đang xử lý.',
            onPressed: () {
              cartController.fetchCart(); 
              if (Get.isRegistered<OrderListController>()) {
                OrderListController.instance.fetchUserOrders();
              }
              Get.offAll(() => const NavigationMenu());
            },
          ));
    } else if (status == 'cancelled') {
      Get.defaultDialog(
        title: "Thanh toán bị hủy",
        middleText: "Bạn đã hủy giao dịch thanh toán.",
        textConfirm: "Đóng",
        confirmTextColor: Colors.white,
        onConfirm: () => Get.back(),
      );
    } else {
      _showError('Thanh toán thất bại. Vui lòng thử lại.');
    }
  }

  /// Hàm tạo đơn hàng chính
  Future<void> processOrder() async {
    // 1. Validate cơ bản
    if (cartController.selectedItems.isEmpty) {
      _showError('Vui lòng chọn sản phẩm để thanh toán');
      return;
    }
    if (addressController.selectedAddress.value == null) {
      _showError('Vui lòng chọn địa chỉ giao hàng');
      return;
    }

    isLoading.value = true;

    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('token');

      if (token == null) {
        _showError('Phiên đăng nhập hết hạn. Vui lòng đăng nhập lại.');
        return;
      }

      // 2. Chuẩn bị dữ liệu Voucher
      // Sử dụng hàm getVouchersForOrder() đã viết trong VoucherController
      // Hàm này trả về Map chuẩn: {"store_id": "CODE", "platform": "CODE", "shipping": "CODE"}
      final vouchersMap = voucherController.getVouchersForOrder();

      // 3. Chuẩn bị Shipping Fee
      // Gửi phí ship gốc (tính toán từ GHTK/GHN...). 
      // Backend sẽ tự trừ nếu có mã voucher 'shipping' trong vouchersMap.
      double shippingFeeToSend = shippingController.shippingFee;

      // 4. Tạo Body Request
      final body = {
        "address_id": addressController.selectedAddress.value!.id,
        "payment_method": selectedPaymentMethod.value, // "COD", "VNPAY", "PAYPAL"
        "shipping_fee": shippingFeeToSend,
        "vouchers": vouchersMap, // Gửi map voucher lên
        "notes": noteController.text.trim(),
        "return_url_scheme": "myapp://payment-return" // Scheme cấu hình trong AndroidManifest/Info.plist
      };

      print("📤 Sending Order Request: ${jsonEncode(body)}");

      // 5. Gọi API
      final response = await http.post(
        Uri.parse('$baseUrl/create/'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token'
        },
        body: json.encode(body),
      );

      print("📥 Response Status: ${response.statusCode}");
      print("📥 Response Body: ${utf8.decode(response.bodyBytes)}");

      // 6. Xử lý kết quả
      if (response.statusCode == 200 || response.statusCode == 201) {
        _handleApiResponse(response);
      } else {
        // Parse lỗi từ server trả về
        final errorData = json.decode(utf8.decode(response.bodyBytes));
        String errorMessage = errorData['error'] ?? 'Tạo đơn hàng thất bại';
        
        // Nếu lỗi liên quan đến voucher, release reservation (nếu có dùng logic reserve)
        await voucherController.releaseAllReservations();
        
        _showError(errorMessage);
      }

    } catch (e) {
      print("❌ Lỗi processOrder: $e");
      _showError('Lỗi kết nối hoặc xử lý: $e');
    } finally {
      isLoading.value = false;
    }
  }

  /// Hàm thanh toán lại cho đơn hàng cũ (Repay)
  Future<void> repayOrder(OrderModel order) async {
    isLoading.value = true;
    try {      
      String endpoint = "";
      
      // Xây dựng URL thanh toán dựa trên rootUrl để tránh hardcode sai IP
      if (order.paymentMethod == "VNPAY") {
         endpoint = "$rootUrl/payments/vnpay/${order.id}/";
      } else if (order.paymentMethod == "PAYPAL") {
         endpoint = "$rootUrl/payments/paypal/${order.id}/";
      } else {
        _showError('Phương thức ${order.paymentMethod} không hỗ trợ thanh toán online lại.');
        return;
      }

      print("🔗 Opening Payment URL: $endpoint");

      if (await canLaunchUrl(Uri.parse(endpoint))) {
         await launchUrl(
           Uri.parse(endpoint), 
           mode: LaunchMode.externalApplication // Mở trình duyệt ngoài để bank app dễ redirect
         );
      } else {
        _showError('Không thể mở trình duyệt thanh toán.');
      }

    } catch (e) {
       print("❌ Lỗi Repay: $e");
      _showError('Lỗi kết nối: $e');
    } finally {
      isLoading.value = false;
    }
  }

  Future<void> _handleApiResponse(http.Response response) async {
      final data = json.decode(utf8.decode(response.bodyBytes));
      final paymentUrl = data['payment_url'];

      // Trường hợp 1: COD hoặc thanh toán tiền mặt -> Thành công ngay
      if (paymentUrl == null || paymentUrl.toString().isEmpty) {
           Get.offAll(() => SuccessScreen(
              image: AppImages.checkoutsuccess,
              title: 'Đặt hàng thành công!',
              subTitle: 'Đơn hàng của bạn đã được tạo. Vui lòng chuẩn bị tiền mặt khi nhận hàng.',
              onPressed: () {
                cartController.fetchCart();
                // Refresh danh sách đơn hàng
                if (Get.isRegistered<OrderListController>()) {
                  OrderListController.instance.fetchUserOrders();
                }
                Get.offAll(() => const NavigationMenu());
              },
            ));
      } 
      // Trường hợp 2: Có link thanh toán (VNPAY/PayPal) -> Mở trình duyệt
      else {
        final uri = Uri.parse(paymentUrl);
        if (await canLaunchUrl(uri)) {
          await launchUrl(uri, mode: LaunchMode.externalApplication);
        } else {
          _showError('Không thể mở liên kết thanh toán.');
        }
      }
  }

  void _showError(String message) {
    Get.snackbar(
      'Thông báo',
      message,
      snackPosition: SnackPosition.BOTTOM,
      backgroundColor: Colors.redAccent.withOpacity(0.1),
      colorText: Colors.red,
      duration: const Duration(seconds: 3),
      margin: const EdgeInsets.all(10),
    );
  }

  /// Hủy đơn hàng
  Future<bool> cancelOrder(int orderId) async {
    isLoading.value = true;
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('token');

      if (token == null) return false;

      final response = await http.post(
        Uri.parse('$baseUrl/$orderId/cancel/'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        Get.snackbar('Thành công', 'Đã hủy đơn hàng thành công', 
          backgroundColor: Colors.green.withOpacity(0.1), colorText: Colors.green);
        
        if (Get.isRegistered<OrderListController>()) {
          OrderListController.instance.fetchUserOrders();
        }
        return true;
      } else {
        final error = json.decode(utf8.decode(response.bodyBytes));
        _showError(error['error'] ?? 'Hủy đơn thất bại');
        return false;
      }
    } catch (e) {
      _showError('Lỗi kết nối: $e');
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  /// Xác nhận đơn hàng (Dành cho Shop/Admin)
  Future<bool> confirmOrder(int orderId) async {
    isLoading.value = true;
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('token');

      if (token == null) return false;

      final response = await http.post(
        Uri.parse('$baseUrl/$orderId/confirm/'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        Get.snackbar('Thành công', 'Đã xác nhận đơn hàng', 
          backgroundColor: Colors.green.withOpacity(0.1), colorText: Colors.green);
        
        if (Get.isRegistered<OrderListController>()) {
          OrderListController.instance.fetchUserOrders();
        }
        return true;
      } else {
        final error = json.decode(utf8.decode(response.bodyBytes));
        _showError(error['error'] ?? 'Xác nhận thất bại');
        return false;
      }
    } catch (e) {
      _showError('Lỗi kết nối: $e');
      return false;
    } finally {
      isLoading.value = false;
    }
  }
}