import 'dart:convert';
import 'package:get/get.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:flutter_app/shop/controllers/cart_controller.dart';
import 'package:flutter_app/shop/controllers/address_controller.dart';
import 'package:flutter_app/common/widgets/success_screen/success_screen.dart';
import 'package:flutter_app/constants/image_string.dart';
import 'package:flutter_app/navigation_menu.dart';

class OrderController extends GetxController {
  static OrderController get instance => Get.find();

  // ✅ SỬA: Dùng late final và khởi tạo bên ngoài constructor hoặc trong onInit
  late final CartController cartController;
  late final AddressController addressController;

  final isLoading = false.obs;
  final selectedPaymentMethod = 'VNPAY'.obs; 
  final String baseUrl = "http://10.0.2.2:8000/api/orders"; 

  @override
  void onInit() {
    super.onInit();
    cartController = Get.put(CartController());
    addressController = Get.put(AddressController()); 
  }

  // ... (Hàm processOrder giữ nguyên) ...
  Future<void> processOrder() async {
    // 1. Validate
    if (cartController.selectedItems.isEmpty) {
      Get.snackbar('Lỗi', 'Vui lòng chọn sản phẩm để thanh toán');
      return;
    }
    if (addressController.selectedAddress.value == null) {
      Get.snackbar('Lỗi', 'Vui lòng chọn địa chỉ giao hàng');
      return;
    }

    isLoading.value = true;


    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('token');

      // 2. Chuẩn bị dữ liệu gửi lên Server
      // Backend cần: items (variant_id, quantity), address_id, payment_method
      final body = {
        "items": cartController.selectedItems.map((item) => {
          "variant_id": item.productId, // Lưu ý: Ở CartItemModel bạn gọi là productId nhưng thực chất là variantId? Kiểm tra lại model nhé.
          // Nếu CartItemModel lưu productId là ID sản phẩm chung, bạn cần sửa CartItemModel để lưu variantId riêng.
          // Giả sử ở đây item.productId chính là variantId (SKU ID).
          "quantity": item.quantity
        }).toList(),
        "address_id": addressController.selectedAddress.value!.id,
        "payment_method": selectedPaymentMethod.value // "VNPAY" hoặc "PAYPAL"
      };

      // 3. Gọi API Tạo Đơn Hàng
      final response = await http.post(
        Uri.parse('$baseUrl/create/'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token'
        },
        body: json.encode(body),
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        final data = json.decode(response.body);
        final paymentUrl = data['payment_url']; // Backend trả về URL thanh toán

        if (paymentUrl != null && paymentUrl.isNotEmpty) {
          // 4. Mở URL thanh toán (VNPAY/PayPal)
          // Logic: Mở trình duyệt -> Người dùng thanh toán -> Redirect về App (Deep Link) hoặc Web Success
          await launchUrl(Uri.parse(paymentUrl), mode: LaunchMode.externalApplication);
          
          // Tạm thời: Chuyển sang màn hình thành công giả định
          // (Thực tế cần Deep Link để hứng callback từ ví điện tử)
          Get.to(() => SuccessScreen(
             image: AppImages.checkoutsuccess,
             title: 'Payment Processing',
             subTitle: 'Please complete payment in browser.',
             onPressed: () => Get.offAll(() => const NavigationMenu()),
          ));
          
          // Xóa giỏ hàng sau khi đặt (logic này nên để Server xử lý khi IPN callback thành công)
          // cartController.clearCart(); 
        } else {
          // Trường hợp COD (Thanh toán khi nhận hàng)
          Get.to(() => SuccessScreen(
             image: AppImages.checkoutsuccess,
             title: 'Order Success',
             subTitle: 'Your order has been placed.',
             onPressed: () => Get.offAll(() => const NavigationMenu()),
          ));
        }
      } else {
        Get.snackbar('Lỗi', 'Server: ${response.body}');
      }
    } catch (e) {
      Get.snackbar('Lỗi', 'Exception: $e');
      print(e);
    } finally {
      isLoading.value = false;
    }
  }
}