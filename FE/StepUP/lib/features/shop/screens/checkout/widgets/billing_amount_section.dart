import 'package:flutter/material.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:get/get.dart';
import 'package:flutter_app/shop/controllers/cart_controller.dart';

class BillingAmountSection extends StatelessWidget {
  const BillingAmountSection({super.key});

  @override
  Widget build(BuildContext context) {
    final controller = Get.put(CartController());

    return Obx(() {
      final subTotal = controller.totalAmount.value;
      final shippingFee = 0.0; // Phí ship cứng (hoặc lấy từ config)
      final taxFee = 0.0; // Thuế (nếu có)
      final total = subTotal + shippingFee + taxFee;

      return Column(
        children: [
          // Subtotal
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Subtotal', style: Theme.of(context).textTheme.bodyMedium),
              Text('\$${subTotal.toStringAsFixed(0)}', style: Theme.of(context).textTheme.bodyMedium),
            ],
          ),
          const SizedBox(height: AppSizes.spaceBtwItems / 2),

          // Shipping
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Shipping Fee', style: Theme.of(context).textTheme.bodyMedium),
              Text('\$${shippingFee.toStringAsFixed(0)}', style: Theme.of(context).textTheme.labelLarge),
            ],
          ),
          
          // Tax (Optional)
          // ...

          const SizedBox(height: AppSizes.spaceBtwItems / 2),

          // Total
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Total', style: Theme.of(context).textTheme.bodyMedium?.copyWith(fontWeight: FontWeight.bold)),
              Text('\$${total.toStringAsFixed(0)}', style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
            ],
          ),
        ],
      );
    });
  }
}