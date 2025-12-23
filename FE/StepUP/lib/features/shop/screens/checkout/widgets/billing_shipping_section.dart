import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/constants/colors.dart';
import 'package:flutter_app/widgets/containers/rounded_container.dart';
import 'package:flutter_app/shop/controllers/shipping_controller.dart';
import 'package:flutter_app/shop/controllers/voucher_controller.dart';

class BillingShippingSection extends StatelessWidget {
  const BillingShippingSection({super.key});

  @override
  Widget build(BuildContext context) {
    final controller = Get.put(ShippingController());
    final voucherController = Get.find<VoucherController>();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text('Phương thức vận chuyển', style: Theme.of(context).textTheme.titleLarge),
            TextButton(
              onPressed: () => controller.selectShippingMethod(context),
              child: const Text('Thay đổi'),
            ),
          ],
        ),
        const SizedBox(height: AppSizes.spaceBtwItems / 2),

        Obx(() {
          if (controller.isLoading.value) return const Center(child: CircularProgressIndicator());
          
          final selectedMethod = controller.selectedShippingMethod.value;
          if (selectedMethod == null) {
            return const Text("Vui lòng chọn đơn vị vận chuyển", style: TextStyle(color: Colors.red));
          }

          // Check if free shipping applied
          final isFree = voucherController.selectedShippingVoucher.value?.isFreeShipping == true;

          return RoundedContainer(
            showBorder: true,
            padding: const EdgeInsets.all(AppSizes.md),
            bgcolor: AppColors.primary.withOpacity(0.05),
            child: Row(
              children: [
                const Icon(Icons.local_shipping_outlined, color: AppColors.primary),
                const SizedBox(width: 10),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          // [FIX]: Bọc Text trong Flexible để tự động xuống dòng hoặc cắt bớt nếu quá dài
                          Flexible(
                            child: Text(
                              selectedMethod.name,
                              style: Theme.of(context).textTheme.bodyLarge,
                              overflow: TextOverflow.ellipsis, // Thêm dấu ... nếu chữ quá dài
                              maxLines: 1, // Chỉ hiện trên 1 dòng
                            ),
                          ),
                            if (isFree) ...[
                              const SizedBox(width: 8),
                              Container(
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 6,
                                  vertical: 2,
                                ),
                                decoration: BoxDecoration(
                                  color: Colors.green,
                                  borderRadius: BorderRadius.circular(4),
                                ),
                                child: const Text(
                                  "FREESHIP",
                                  style: TextStyle(
                                    color: Colors.white,
                                    fontSize: 10,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              )
                            ]
                          ],
                        ),
                      Text("Giao hàng: ${selectedMethod.estimatedDays}", style: Theme.of(context).textTheme.bodySmall),
                    ],
                  ),
                ),
                Text(
                  isFree ? "Miễn phí" : "\$${selectedMethod.fee.toStringAsFixed(0)}", 
                  style: Theme.of(context).textTheme.titleMedium?.apply(color: isFree ? Colors.green : null)
                ),
              ],
            ),
          );
        }),
      ],
    );
  }
}