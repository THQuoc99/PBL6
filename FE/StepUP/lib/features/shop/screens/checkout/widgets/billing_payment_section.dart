import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/constants/colors.dart';
import 'package:flutter_app/components/rounded_container.dart';
import 'package:flutter_app/screens/home/components/section_heading.dart';
import 'package:flutter_app/shop/controllers/order_controller.dart';

class BillingPaymentSection extends StatelessWidget {
  const BillingPaymentSection({super.key});

  @override
  Widget build(BuildContext context) {
    final controller = Get.put(OrderController());

    return Column(
      children: [
        SectionHeading(
          title: 'Phương thức thanh toán', 
          buttonTitle: 'Thay đổi', 
          onButtonPressed: () {
             // Hiển thị Modal chọn phương thức
             _showPaymentModal(context, controller);
          },
        ),
        const SizedBox(height: AppSizes.spaceBtwItems / 2),
        
        Obx(() => Row(
          children: [
            RoundedContainer(
              width: 60,
              height: 35,
              bgcolor: AppColors.light,
              padding: const EdgeInsets.all(AppSizes.sm),
              child: Image.asset(
                 _getPaymentIcon(controller.selectedPaymentMethod.value), 
                 fit: BoxFit.contain
              ),
            ),
            const SizedBox(width: AppSizes.spaceBtwItems / 2),
            Text(controller.selectedPaymentMethod.value, style: Theme.of(context).textTheme.bodyLarge),
          ],
        )),
      ],
    );
  }

  String _getPaymentIcon(String method) {
    switch (method) {
      case 'PAYPAL': return 'assets/images/payments/paypal.png';
      case 'VNPAY': return 'assets/images/payments/vnpay.png';
      default: return 'assets/images/payments/cod.jpg';
    }
  }

  void _showPaymentModal(BuildContext context, OrderController controller) {
    showModalBottomSheet(
      context: context,
      builder: (_) => Padding(
        padding: const EdgeInsets.all(AppSizes.defaultSpace),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SectionHeading(title: 'Chọn phương thức thanh toán', showActionButton: false),
            const SizedBox(height: AppSizes.spaceBtwItems),
            _buildPaymentOption(context, controller, 'VNPAY', 'VNPAY E-Wallet'),
            _buildPaymentOption(context, controller, 'PAYPAL', 'PayPal'),
            _buildPaymentOption(context, controller, 'COD', 'Thanh toán khi nhận hàng'),
          ],
        ),
      ),
    );
  }

  Widget _buildPaymentOption(BuildContext context, OrderController controller, String value, String title) {
    return ListTile(
      onTap: () {
        controller.selectedPaymentMethod.value = value;
        Navigator.pop(context);
      },
      leading: const Icon(Icons.payment), // Hoặc ảnh logo
      title: Text(title, style: Theme.of(context).textTheme.bodyLarge),
      trailing: Obx(() => controller.selectedPaymentMethod.value == value 
          ? const Icon(Icons.check_circle, color: AppColors.primary) 
          : const SizedBox()),
    );
  }
}