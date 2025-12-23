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
    final voucherController = Get.put(VoucherController());

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Header
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Phương thức vận chuyển',
              style: Theme.of(context).textTheme.bodyLarge,
            ),
            TextButton(
              onPressed: () => controller.selectShippingMethod(context),
              child: const Text('Thay đổi'),
            ),
          ],
        ),
        const SizedBox(height: AppSizes.spaceBtwItems / 2),

        // Selected Shipping Method Display
        Obx(() {
          if (controller.isLoading.value) {
            return const Center(
              child: Padding(
                padding: EdgeInsets.all(AppSizes.md),
                child: CircularProgressIndicator(),
              ),
            );
          }

          final selectedMethod = controller.selectedShippingMethod.value;
          final selectedVoucher = voucherController.selectedVoucher.value;

          bool voucherMakesFreeShip = false;
          if (selectedVoucher != null && selectedMethod != null) {
            if (selectedVoucher.discountType == 'fixed') {
              try {
                if (selectedVoucher.discountValue >= selectedMethod.fee) voucherMakesFreeShip = true;
              } catch (_) {}
            }
          }

          if (selectedMethod == null) {
            return InkWell(
              onTap: () => controller.selectShippingMethod(context),
              child: RoundedContainer(
                showBorder: true,
                padding: const EdgeInsets.all(AppSizes.md),
                borderColor: AppColors.primary,
                bgcolor: Colors.transparent,
                child: Row(
                  children: [
                    const Icon(Icons.local_shipping, color: AppColors.primary),
                    const SizedBox(width: AppSizes.spaceBtwItems),
                    Text(
                      'Chọn phương thức vận chuyển',
                      style: Theme.of(context).textTheme.bodyMedium!.apply(
                            color: AppColors.primary,
                            fontWeightDelta: 1,
                          ),
                    ),
                    const Spacer(),
                    const Icon(Icons.arrow_forward_ios, size: 16),
                  ],
                ),
              ),
            );
          }

          // Display selected method
          return RoundedContainer(
            showBorder: true,
            padding: const EdgeInsets.all(AppSizes.md),
            bgcolor: AppColors.primary.withOpacity(0.05),
            borderColor: AppColors.primary,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Icon(Icons.local_shipping_outlined,
                        color: AppColors.primary, size: 20),
                    const SizedBox(width: AppSizes.spaceBtwItems),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Text(
                                selectedMethod.name,
                                style: Theme.of(context).textTheme.titleMedium,
                              ),
                              if (selectedMethod.isFreeShip || voucherMakesFreeShip) ...[
                                const SizedBox(width: 8),
                                Container(
                                  padding: const EdgeInsets.symmetric(
                                    horizontal: 8,
                                    vertical: 2,
                                  ),
                                  decoration: BoxDecoration(
                                    color: Colors.green,
                                    borderRadius: BorderRadius.circular(4),
                                  ),
                                  child: const Text(
                                    'FREESHIP',
                                    style: TextStyle(
                                      color: Colors.white,
                                      fontSize: 10,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ),
                              ],
                            ],
                          ),
                          const SizedBox(height: 4),
                          Text(
                            selectedMethod.description,
                            style: Theme.of(context).textTheme.bodySmall,
                          ),
                        ],
                      ),
                    ),
                    Text(
                      (selectedMethod.isFreeShip || voucherMakesFreeShip)
                          ? 'Miễn phí'
                          : '\$${selectedMethod.fee.toStringAsFixed(0)}',
                      style: Theme.of(context).textTheme.titleMedium!.apply(
                            color: (selectedMethod.isFreeShip || voucherMakesFreeShip)
                                ? Colors.green
                                : AppColors.primary,
                            fontWeightDelta: 2,
                          ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Row(
                  children: [
                    const Icon(Icons.access_time, size: 14, color: Colors.grey),
                    const SizedBox(width: 4),
                    Text(
                      'Dự kiến: ${selectedMethod.estimatedDays}',
                      style: Theme.of(context).textTheme.bodySmall!.apply(
                            color: Colors.grey,
                          ),
                    ),
                  ],
                ),
              ],
            ),
          );
        }),
      ],
    );
  }
}

