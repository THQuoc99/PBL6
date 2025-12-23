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
  late AppLinks _appLinks;
  StreamSubscription<Uri>? _linkSubscription;

  final isLoading = false.obs;
  final selectedPaymentMethod = 'VNPAY'.obs;
  final noteController = TextEditingController();

  final String baseUrl = "http://10.0.2.2:8000/api/orders";

  @override
  void onInit() {
    super.onInit();
    cartController = Get.put(CartController());
    addressController = Get.put(AddressController());
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
    String status = uri.queryParameters['status'] ?? '';
    String vnpResponseCode = uri.queryParameters['vnp_ResponseCode'] ?? '';

    if (status == 'success' || vnpResponseCode == '00') {
      Get.to(() => SuccessScreen(
            image: AppImages.checkoutsuccess,
            title: 'Thanh toán thành công!',
            subTitle: 'Đơn hàng của bạn đã được xác nhận.',
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
        middleText: "Giao dịch chưa hoàn tất.",
        textConfirm: "Đóng",
        onConfirm: () => Get.back(),
      );
    } else {
      _showError('Thanh toán thất bại hoặc bị lỗi.');
    }
  }

  Future<void> processOrder() async {
    if (cartController.selectedItems.isEmpty) {
      _showError('Vui lòng chọn sản phẩm');
      return;
    }

    isLoading.value = true;

    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('token');

      if (token == null) {
        _showError('Bạn chưa đăng nhập');
        return;
      }

      final shippingController = Get.find<ShippingController>();
      final voucherController = Get.find<VoucherController>();

      // Tính subtotal theo store để back-end áp voucher per-store
      final Map<String, double> storeSubtotals = {};
      for (var item in cartController.selectedItems) {
        final sid = item.storeId ?? 'unknown';
        storeSubtotals[sid] = (storeSubtotals[sid] ?? 0) + item.subTotal;
      }

      // Nếu user đã chọn voucher thủ công, dùng voucher đó; nếu không thì chọn tự động
      Map<String, String> vouchersMap = {};
      final selected = voucherController.selectedVoucher.value;
      if (selected != null) {
        if (selected.type == 'platform') {
          vouchersMap['platform'] = selected.code;
        } else {
          // apply as store voucher to all stores if applicable, otherwise try to map by seller id
          if (selected.applicableStores != null && selected.applicableStores!.isNotEmpty) {
            for (final sid in selected.applicableStores!) {
              vouchersMap['$sid'] = selected.code;
            }
          } else if (selected.id != null && selected.type == 'store') {
            // fallback: apply to first store in cart that matches voucher.seller
            for (final sid in storeSubtotals.keys) {
              vouchersMap[sid] = selected.code;
            }
          }
        }
      } else {
        // Chọn voucher tự động nếu có
        // Ensure shipping fee is calculated so autoApplyBest can evaluate shipping vouchers
        try {
          await shippingController.calculateShippingFee();
        } catch (_) {}
        vouchersMap = await voucherController.autoApplyBest(storeSubtotals);

        // Reflect auto-applied selection in UI/controllers so user sees selected platform/shipping/store vouchers
        if (vouchersMap.isNotEmpty) {
          // platform
          final pcode = vouchersMap['platform'];
          if (pcode != null) {
            final vm = voucherController.vouchers.firstWhereOrNull((v) => v.code == pcode) ?? voucherController.myVouchers.firstWhereOrNull((v) => v.code == pcode);
            if (vm != null) voucherController.selectedVoucher.value = vm;
          }
          // shipping
          final scode = vouchersMap['shipping'];
          if (scode != null) {
            final sm = voucherController.vouchers.firstWhereOrNull((v) => v.code == scode) ?? voucherController.myVouchers.firstWhereOrNull((v) => v.code == scode);
            if (sm != null) voucherController.selectedShipping.value = sm;
          }
          // store vouchers
          for (final entry in vouchersMap.entries) {
            final key = entry.key;
            if (key == 'platform' || key == 'shipping') continue;
            final code = entry.value;
            final vm = voucherController.vouchers.firstWhereOrNull((v) => v.code == code) ?? voucherController.myVouchers.firstWhereOrNull((v) => v.code == code);
            if (vm != null) voucherController.selectedStoreVouchers[key] = vm;
          }
          voucherController.selectedStoreVouchers.refresh();
        }
      }

      // Include any manually selected store vouchers and shipping voucher
      // selectedStoreVouchers keys are store ids
      for (final entry in voucherController.selectedStoreVouchers.entries) {
        vouchersMap[entry.key] = entry.value.code;
      }
      final selectedShipping = voucherController.selectedShipping.value;
      if (selectedShipping != null) {
        // Prefer explicit shipping voucher key when voucher type is 'shipping' or it is marked freeship
        if (selectedShipping.type == 'shipping' || selectedShipping.isFreeShipping == true) {
          vouchersMap['shipping'] = selectedShipping.code;
        } else if (selectedShipping.type == 'platform') {
          // If no platform voucher yet and shipping is platform-type, apply to platform
          if (!vouchersMap.containsKey('platform')) {
            vouchersMap['platform'] = selectedShipping.code;
          } else {
            // otherwise add as a separate key so backend can inspect it if supports
            vouchersMap['platform_shipping'] = selectedShipping.code;
          }
        } else {
          // assign to applicable stores or all
          if (selectedShipping.applicableStores != null && selectedShipping.applicableStores!.isNotEmpty) {
            for (final sid in selectedShipping.applicableStores!) {
              vouchersMap['$sid'] = selectedShipping.code;
            }
          } else {
            for (final sid in storeSubtotals.keys) {
              vouchersMap[sid] = selectedShipping.code;
            }
          }
        }
      }

      // Reserve các voucher đã chọn để tránh race (unique codes only)
      final reservedIds = <int>[];
      final codesToReserve = vouchersMap.values.toSet();
      for (final code in codesToReserve) {
        final rid = await voucherController.reserveVoucher(code, seconds: 300);
        if (rid != null) reservedIds.add(rid);
      }

      // Determine shipping fee to send. Prefer backend-validated shipping voucher reductions.
      double shippingFeeToSend = shippingController.shippingFee;
      // If a shipping-specific voucher was selected/auto-applied, ask backend how much it reduces.
      if (vouchersMap.containsKey('shipping')) {
        final scode = vouchersMap['shipping']!;
        try {
          final check = await voucherController.checkVoucher(scode, null, target: 'shipping', shippingFee: shippingFeeToSend);
          if (check != null && check['valid'] == true) {
            final dam = check['discount_amount'];
            double reduction = 0.0;
            if (dam is num) reduction = dam.toDouble(); else reduction = double.tryParse('$dam') ?? 0.0;
            shippingFeeToSend = (shippingFeeToSend - reduction).clamp(0.0, double.infinity);
          }
        } catch (e) {
          print('Error checking shipping voucher $scode: $e');
        }
      } else if (vouchersMap.containsKey('platform')) {
        // As a fallback, allow platform voucher to reduce shipping only if backend confirms it (target=shipping)
        final pcode = vouchersMap['platform']!;
        try {
          final checkP = await voucherController.checkVoucher(pcode, null, target: 'shipping', shippingFee: shippingFeeToSend);
          if (checkP != null && checkP['valid'] == true) {
            final dam = checkP['discount_amount'];
            double reduction = 0.0;
            if (dam is num) reduction = dam.toDouble(); else reduction = double.tryParse('$dam') ?? 0.0;
            shippingFeeToSend = (shippingFeeToSend - reduction).clamp(0.0, double.infinity);
          }
        } catch (e) {
          print('Error checking platform-as-shipping $pcode: $e');
        }
      }

      final body = {
        "address_id": addressController.selectedAddress.value!.id,
        "payment_method": selectedPaymentMethod.value,
        "shipping_fee": shippingFeeToSend,
        "vouchers": vouchersMap,
        "notes": noteController.text.trim(),
        "return_url_scheme": "myapp://payment-return"
      };

      final response = await http.post(
        Uri.parse('$baseUrl/create/'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token'
        },
        body: json.encode(body),
      );

      if (response.statusCode != 200 && response.statusCode != 201) {
        // release reservations on failure
        await voucherController.releaseAllReservations();
      }

      _handleApiResponse(response);

    } catch (e) {
      print("Lỗi processOrder: $e");
      _showError('Có lỗi xảy ra khi xử lý đơn hàng');
    } finally {
      isLoading.value = false;
    }
  }

  // ✅ FIX LỖI 2: Thêm hàm repayOrder vào đây
  Future<void> repayOrder(OrderModel order) async {
    isLoading.value = true;
    try {      
      String endpoint = "";
      if (order.paymentMethod == "VNPAY") {
         endpoint = "http://10.0.2.2:8000/payments/vnpay/${order.id}/";
      } else if (order.paymentMethod == "PAYPAL") {
         endpoint = "http://10.0.2.2:8000/payments/paypal/${order.id}/";
      }

      if (endpoint.isNotEmpty) {
         if (!await launchUrl(Uri.parse(endpoint), mode: LaunchMode.externalApplication)) {
            _showError('Không thể mở trình duyệt thanh toán.');
         }
      } else {
        _showError('Phương thức thanh toán không hỗ trợ trả lại.');
      }

    } catch (e) {
       print("Lỗi Repay: $e");
      _showError('Lỗi kết nối: $e');
    } finally {
      isLoading.value = false;
    }
  }

  Future<void> _handleApiResponse(http.Response response) async {
      if (response.statusCode == 200 || response.statusCode == 201) {
        final data = json.decode(utf8.decode(response.bodyBytes));
        final paymentUrl = data['payment_url'];

        if (paymentUrl == null || paymentUrl.isEmpty) {
             Get.to(() => SuccessScreen(
                image: AppImages.checkoutsuccess,
                title: 'Thành công',
                subTitle: 'Đơn hàng COD đã tạo thành công.',
                onPressed: () {
                  cartController.fetchCart();
                  // Refresh order list
                  if (Get.isRegistered<OrderListController>()) {
                    OrderListController.instance.fetchUserOrders();
                  }
                  Get.offAll(() => const NavigationMenu());
                },
              ));
        } else {
          final uri = Uri.parse(paymentUrl);
          bool launched = await launchUrl(uri, mode: LaunchMode.externalApplication);
          if (!launched) _showError('Không thể mở trình duyệt thanh toán.');
        }
      } else {
        _showError('Lỗi server: ${response.body}');
      }
  }

  void _showError(String message) {
    print('❌ OrderController Error: $message');
  }

  /// Cancel order
  Future<bool> cancelOrder(int orderId) async {
    isLoading.value = true;
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('token');

      if (token == null) {
        print('❌ Cancel order: Not logged in');
        return false;
      }

      final response = await http.post(
        Uri.parse('$baseUrl/$orderId/cancel/'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        print('✅ Order cancelled successfully');
        
        // Refresh order list
        if (Get.isRegistered<OrderListController>()) {
          OrderListController.instance.fetchUserOrders();
        }
        return true;
      } else {
        final error = json.decode(response.body);
        print('❌ Cancel order failed: ${error['error'] ?? 'Unknown error'}');
        return false;
      }
    } catch (e) {
      print('❌ Cancel order error: $e');
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  /// Confirm order (Shop only)
  Future<bool> confirmOrder(int orderId) async {
    isLoading.value = true;
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('token');

      if (token == null) {
        print('❌ Confirm order: Not logged in');
        return false;
      }

      final response = await http.post(
        Uri.parse('$baseUrl/$orderId/confirm/'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        print('✅ Order confirmed successfully');
        
        // Refresh order list
        if (Get.isRegistered<OrderListController>()) {
          OrderListController.instance.fetchUserOrders();
        }
        return true;
      } else {
        final error = json.decode(response.body);
        print('❌ Confirm order failed: ${error['error'] ?? 'Unknown error'}');
        return false;
      }
    } catch (e) {
      print('❌ Confirm order error: $e');
      return false;
    } finally {
      isLoading.value = false;
    }
  }
}